# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from nifiapi.properties import PropertyDescriptor
from nifiapi.properties import StandardValidators
from nifiapi.properties import ExpressionLanguageScope
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult

from evernote.api.client import EvernoteClient
import evernote.edam.userstore.constants as UserStoreConstants

import xml.etree.ElementTree as ET
from xml.dom import minidom

from datetime import datetime, timezone
import os
import re




class ExportNotesFromEvernote(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']
    class ProcessorDetails:
        dependencies = ['evernote3', 'oauth2' ]
        version = '0.0.1-SNAPSHOT'
        description = 'Perform a full export of Notes from your Evernote or incrementally exports based on from export date/time. The exported notes are written to a configured location as an enex format. '
        tags = ['Evernote']


    def __init__(self, **kwargs):
        # Build Property Descriptors
        self.evernote_auth_token= PropertyDescriptor(
            name="Evernote Authentication Token",
            description="The API key to connect to Evernote API",
            required = True,
            sensitive = True
        )

        self.export_directory= PropertyDescriptor(
            name="Export Directory",
            description="The full path to a directory where the Notes will be exported to",
            required=True,
        )

        self.stack_filter = PropertyDescriptor(
            name="Stack Filter",
            description="A set of notebook stacks to only export Notes from.",
            required=False,
        )


        self.export_from_dtm = PropertyDescriptor(
            name="Export from Date/Time",
            description="The initial date/time that you want to export all notes from. The date format should be YYYY-MM-DD HH:MM:SS (e.g: 2023-06-01 12:00:00). If no date is specified. Then all notes will be exported "
        )



        self.descriptors = [self.evernote_auth_token, self.export_directory, self.stack_filter, self.export_from_dtm]

    def onScheduled(self, context):
        self.logger.info("Initializing Evernote Store")

        # Get the properties from the processor needed to configure the OpenAI Embedding Service
        evernote_auth_token = context.getProperty(self.evernote_auth_token.name).getValue()

        client = EvernoteClient(token=evernote_auth_token, sandbox=False, china=False)
        user_store = client.get_user_store()
        version_ok = user_store.checkVersion(
            "Evernote EDAMTest (Python)",
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR
        )
        self.logger.info("Is my Evernote API version up to date: " +  str(version_ok))

        self.note_store = client.get_note_store()

        export_from_dtm_string = context.getProperty(self.export_from_dtm.name).getValue()
        if export_from_dtm_string is None or export_from_dtm_string == '':
            # if date not set, then set date so that all notes will be exported.
            export_from_dtm_string = '1980-03-26 12:00:00'
            self.logger.info("Export from dtm being reset to beginning: " + export_from_dtm_string)

        # Convert string to a datatime and then to timestamp
        dt_object = datetime.strptime(export_from_dtm_string, "%Y-%m-%d %H:%M:%S")
        self.export_from_dtm_timestamp_window = int(dt_object.timestamp())

        self.logger.info(f" The export from dtm that is initally set is timestamp[ {self.export_from_dtm_timestamp_window}] with string format[{export_from_dtm_string}]")

    def escape_filename(self, filename):
        # Replace any characters that are not allowed in filenames with an underscore (_)
        escaped_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return escaped_filename

    def retrieve_all_notebooks(self, stack_filter=None):
        # Retrieve all notebooks
        notebooks = self.note_store.listNotebooks()
        if (stack_filter is None):
            return notebooks
        else:
            notebooks_in_stack = [notebook for notebook in notebooks if notebook.stack == stack_filter]
            return notebooks_in_stack



    def exportNotes(self, notebooks, output_directory, export_from_dtm_timestamp):
        # Iterate over each notebook
        failed_notes = []
        exported_note_count = 0

        self.logger.info("The export from dtm that is used for this run is:: " + datetime.fromtimestamp(export_from_dtm_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"))

        for notebook in notebooks:
            notebook_name = notebook.name
            self.logger.info("Processing notebook:"+ notebook_name)

            # Set up note filter to retrieve all notes in the notebook
            note_filter = NoteFilter()
            note_filter.notebookGuid = notebook.guid
            note_filter.updated = export_from_dtm_timestamp

            # Set up result spec to retrieve the note content
            result_spec = NotesMetadataResultSpec(includeTitle=True, includeTagGuids=True, includeUpdated=True,
                                                  includeCreated=True)

            # Retrieve the metadata for all notes in the notebook
            offset = 0
            page_size = 100
            total_notes_in_notebook_exported = 0
            while True:

                notes_metadata = self.note_store.findNotesMetadata(note_filter, offset, page_size, result_spec)
                for note_metadata in notes_metadata.notes:
                    note_guid = note_metadata.guid
                    note_title = note_metadata.title
                    # The date returned from evernote has millisconed precision but we need to remove it to compare against python date from seconds
                    note_updated_dtm = note_metadata.updated / 1000

                    if note_updated_dtm < export_from_dtm_timestamp:
                        # self.logger.info("Note "+ note_title +" was last updated " + note_updated_dtm + " before the specified datetime " + export_from_dtm_timestamp + "..Skipping...")
                        continue

                    # Retrieve the note content
                    try:
                        note = self.note_store.getNote(note_guid, True, True, True, True)
                        tag_names = self.note_store.getNoteTagNames(note_guid)
                    except Exception as e:
                        self.logger.info("Error occurred while retrieving note["+note_title+"]")
                        failed_notes.append(note_title)
                        continue

                    # Access note metadata
                    note_title = note.title
                    note_created = datetime.fromtimestamp(note.created / 1000).strftime("%Y%m%dT%H%M%SZ")
                    note_updated = datetime.fromtimestamp(note.updated / 1000).strftime("%Y%m%dT%H%M%SZ")

                    self.logger.info("Exporting note with title: "+ note_title)

                    note_attributes = note.attributes

                    # Access the Content
                    note_content = note.content

                    # Create the root element for the XML
                    root = ET.Element("en-export")
                    root.set("export-date", datetime.now().strftime("%Y%m%dT%H%M%SZ"))
                    root.set("application", "Evernote")
                    root.set("version", "10.44.8")

                    # Create the note element
                    note_elem = ET.SubElement(root, "note")

                    # Create the title element
                    title_elem = ET.SubElement(note_elem, "title")
                    title_elem.text = f"{notebook.name} - {note_title}"

                    # Create the created element
                    created_elem = ET.SubElement(note_elem, "created")
                    created_elem.text = note_created

                    # Create the updated element
                    updated_elem = ET.SubElement(note_elem, "updated")
                    updated_elem.text = note_updated

                    # Create the tags element . If empty still have the element with just just empty value
                    tags_elem = ET.SubElement(note_elem, "tags")
                    if len(tag_names) == 0:
                        tag_names = [' ']
                    tags_elem.text = ','.join(tag_names)

                    # Create the content element
                    content_elem = ET.SubElement(note_elem, "content")
                    content_elem.text = note_content

                    # Create the XML tree
                    tree = ET.ElementTree(root)

                    # Convert the XML tree to a formatted string
                    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

                    # Specify the output file path
                    file_name = f"Notebook[{notebook.name}]__Note[{note_title}]__Id[{note_guid[-4:]}].enex"
                    escaped_file_named= self.escape_filename(file_name)
                    output_path = os.path.join(output_directory, escaped_file_named)

                    # Save the XML content to a file
                    with open(output_path, "w", encoding="utf-8") as file:
                        file.write(xml_string)

                    exported_note_count += 1
                    total_notes_in_notebook_exported += 1
                    self.logger.info("Note[" + note_title +"] in notebook["+notebook.name+"]  saved to: " + output_path)

                if len(notes_metadata.notes) < page_size:
                    self.logger.info(" Finished exporting " + str(total_notes_in_notebook_exported) + " notes from notebook " + notebook.name)
                    break
                offset += page_size

        self.logger.info("Export completed. Number of notes exported successfuly is: "+ str(exported_note_count))
        self.logger.info("Number of notes failed is " +  str(len(failed_notes)))


    def transform(self, context, flowFile):

        self.logger.info("Inside Transform of ExportNOtesFromEvernote....")
        # Capture the current date/time for moving time window
        current_dtm = datetime.now()
        #Fetch all the note notebooks in the account
        stack_filter = context.getProperty(self.stack_filter.name).getValue()

        notebooks = self.retrieve_all_notebooks(stack_filter)
        self.logger.info("Number of notebooks in  account is: " + str(len(notebooks)))

        output_directory = context.getProperty(self.export_directory.name).getValue()

        self.exportNotes(notebooks, output_directory, self.export_from_dtm_timestamp_window)

        # Update the export from date once the the export run is complete. Convert datetime and then to  timestamp
        self.export_from_dtm_timestamp_window = int(current_dtm.timestamp())

        return FlowFileTransformResult(relationship="success")


    def getPropertyDescriptors(self):
        return self.descriptors
