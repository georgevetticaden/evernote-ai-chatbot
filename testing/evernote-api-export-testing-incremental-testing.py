import os
import re
import time
from evernote.api.client import EvernoteClient
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types

import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.ttypes as NoteTypes
from evernote.api.client import EvernoteClient
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta
import os

from datetime import datetime, timezone


def retrieve_all_notebooks(note_store, stack_filter=None):
    # Retrieve all notebooks
    notebooks = note_store.listNotebooks()
    if(stack_filter is None):
        return notebooks
    else:
        notebooks_in_stack = [notebook for notebook in notebooks if notebook.stack == stack_filter ]
        return notebooks_in_stack


def get_note_store(sandbox):
    global client

    if sandbox is True:
        auth_token = os.environ['EVERNOTE_SANDBOX_AUTH_TOKEN']
    else:
        auth_token = os.environ['EVERNOTE_PROD_AUTH_TOKEN']

    client = EvernoteClient(token=auth_token, sandbox=sandbox, china=False)
    user_store = client.get_user_store()
    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR
    )
    print("Is my Evernote API version up to date? ", str(version_ok))
    print("")
    if not version_ok:
        exit(1)
    return client.get_note_store()

# Define a function to escape special characters in a string
def escape_filename(filename):
    # Replace any characters that are not allowed in filenames with an underscore (_)
    escaped_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return escaped_filename

def exportNotes(notebooks, output_directory, export_from_dtm_string):
    # Iterate over each notebook
    failed_notes = []
    exported_note_count = 0

    # Convert from string to timestamp
    # Convert string to a timestamp
    dt_object = datetime.strptime(export_from_dtm_string, "%Y-%m-%d %H:%M:%S")
    export_from_dtm_timestamp_window = int(dt_object.timestamp())


    print("dtm converted to timestamp is: " + datetime.fromtimestamp(export_from_dtm_timestamp_window).strftime("%Y-%m-%d %H:%M:%S"))

    for notebook in notebooks:
        notebook_name = notebook.name
        print("Processing notebook:", notebook_name)

        # Set up note filter to retrieve all notes in the notebook
        note_filter = NoteFilter()
        note_filter.notebookGuid = notebook.guid
        note_filter.updated = export_from_dtm_timestamp_window

        # Set up result spec to retrieve the note content
        result_spec = NotesMetadataResultSpec(includeTitle=True, includeTagGuids=True, includeUpdated=True, includeCreated=True)

        # Retrieve the metadata for all notes in the notebook
        offset = 0
        page_size = 100
        total_notes_in_notebook_exported = 0
        while True:
            notes_metadata = note_store.findNotesMetadata(note_filter, offset, page_size, result_spec)
            for note_metadata in notes_metadata.notes:
                note_guid = note_metadata.guid
                note_title = note_metadata.title
                # The date returned from evernote has millisconed precision but we need to remove it to compare against pyuthon date from seconds
                note_updated_dtm = note_metadata.updated / 1000
                if note_updated_dtm< export_from_dtm_timestamp_window:
                    # print(f"Note '{note_title}' was last updated{note.updated} before the specified datetime {export_from_dtm_timestamp}. Skipping...")
                    continue


                # Retrieve the note content
                try:
                    note = note_store.getNote(note_guid, True, True, True, True)
                    tag_names = note_store.getNoteTagNames(note_guid)
                except Exception as e:
                    print(f"Error occurred while retrieving note[{note_title}] with error:  {e}")
                    failed_notes.append(note_title)
                    continue

                # Access note metadata
                note_title = note.title
                note_created = datetime.fromtimestamp(note.created / 1000).strftime("%Y%m%dT%H%M%SZ")
                note_updated = datetime.fromtimestamp(note.updated / 1000).strftime("%Y%m%dT%H%M%SZ")


                print("Exporting note with title:", note_title)

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

                # # Create the note-attributes element
                # note_attributes_elem = ET.SubElement(note_elem, "note-attributes")
                # for key, value  in note_attributes.__dict__.items():
                #     if value is not None:
                #         note_attribute_element = ET.SubElement(note_attributes_elem, key)
                #         note_attribute_element.text = str(value)

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
                file_name = f"Notebook__{notebook.name}__Note__{note_title}__Id__{note_guid[-4:]}.enex"

                escaped_file_named = escape_filename(file_name)
                output_path = os.path.join(output_directory, escaped_file_named)

                # Save the XML content to a file
                with open(output_path, "w", encoding="utf-8") as file:
                    file.write(xml_string)

                exported_note_count+=1
                total_notes_in_notebook_exported+=1
                print(f"Note '{note_title}' in notebook '{notebook.name}' saved to '{output_path}'")

            if len(notes_metadata.notes) < page_size:
                print(f"********* Finished exporting '{total_notes_in_notebook_exported}' notes from notebook '{notebook.name}")
                break
            offset += page_size

    print(f"Export completed. Number of notes exported successfuly is [{exported_note_count}]")
    print(f"Number of notes failed is [{str(len(failed_notes))}]")
    print("Failed Notes:")
    print(failed_notes)

# Authenticate and get handle to note store
note_store = get_note_store(sandbox=False)

#Fetch all the note notebooks in the account
notebooks = retrieve_all_notebooks(note_store, stack_filter='Home')
print("Number of notebooks in  account is: " + str(len(notebooks)))
# print(notebooks)

# Export Notes
output_directory = '/Users/aju/Dev-Testing/evernotes'
export_dtm = '2023-06-21 12:00:00'
exportNotes(notebooks, output_directory=output_directory, export_from_dtm_string=export_dtm)


# Export Notes from current date and 2 mins before
# output_directory = '/Users/aju/Dev-Testing/evernotes'
# current_dtm = datetime.now()
# two_mins_before = current_dtm - timedelta(minutes=2)
# two_mins_before_dtm_timestamp = int(two_mins_before.timestamp())
# two_mins_before_date_string = datetime.fromtimestamp(two_mins_before_dtm_timestamp).strftime("%Y-%m-%d %H:%M:%S")
# print(two_mins_before_date_string)
# exportNotes(notebooks, output_directory=output_directory, export_from_dtm_string=two_mins_before_date_string)