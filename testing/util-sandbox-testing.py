from datetime import datetime, timezone

from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chains import ConversationChain

import ast



# string_of_tuples= """('When did my elbow pain occur?', 'The right elbow pain occurred on January 11, 2023.\nSOURCES: /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Right Elbow Pain - 01-11-23_77bd1ddc-a2f4-ff71-f982-c8e00b99c8ff.enex'), ('What was the cause and what did the doctor suggest?', 'The cause of the right elbow pain is elbow bursitis. The doctor suggested seeing an orthopedic to extract the fluid and test, and if it happens again, to come in within 24 hours to see if they can extract the fluid. The doctor also suggested waiting for 3 more months and seeing if the pain goes away with therapy before considering a cortisone shot or something else. \nSOURCES: /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Right Elbow Pain - 01-11-23_77bd1ddc-a2f4-ff71-f982-c8e00b99c8ff.enex, /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Appointment with Dr. Patel on 7_11 for Right Elblow Pain_670413eb-c656-96cd-4a60-57e57faf2372.enex, /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Meeting with Dr. Patel - Ortho - 6-28-22_2aa4a604-8676-72d3-e6c7-1e95d3218bc6.enex, /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_CAll with Dr. Patel on Elbow - 1_31_23_41485090-e28e-0d1f-e759-b06618097958.enex'), ('Where did i go for physical therapy for the pain?', 'The physical therapy location recommended for the right elbow pain is Achieve Physical Therapy located at 1315 Macon Drive, Suite 105, Naperville, IL 60564. \nSOURCES: /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Physical Therapy for Elbow_dc5108b8-a13e-935a-8b82-3379af4b600a.enex, /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Appointment with Dr. Patel on 7_11 for Right Elblow Pain_670413eb-c656-96cd-4a60-57e57faf2372.enex'), ('What is the address?', 'The address for Achieve Physical Therapy recommended for right elbow pain is 1315 Macom Drive, Suite 105, Naperville, IL 60564. \nSOURCES: /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Physical Therapy for Elbow_dc5108b8-a13e-935a-8b82-3379af4b600a.enex, /Users/aju/Dev-Testing/evernotes//Family_ Aju_ Health_Meeting with Dr. Patel - Ortho - 6-28-22_2aa4a604-8676-72d3-e6c7-1e95d3218bc6.enex')"""
# # string_of_tuples='()'
# escaped_string = string_of_tuples.replace('\n', '-' )
#
# print(escaped_string)
#
#
# array_of_tuples = ast.literal_eval('[' + escaped_string + ']')
#
# print(len(array_of_tuples))
#
# print(array_of_tuples)
#
# print("********************************")
#
# # print(array_of_tuples[0])
# # print("********************************")
# # print(array_of_tuples[1])
# # print("********************************")
# # print(array_of_tuples[2])
#
#

# date_string = "2023-06-21 12:00:00"
#
#
# dt_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
# timestamp = int(dt_object.timestamp())
#
# revert = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
# print(revert)


# current_dtm = datetime.now()
# current_timestamp = int(current_dtm.timestamp())
#
# current_date_string = datetime.fromtimestamp(current_timestamp).strftime("%Y-%m-%d %H:%M:%S")
# print(current_date_string)


timestamp_int = 1687457368
print( datetime.fromtimestamp(timestamp_int).strftime("%Y-%m-%d %H:%M:%S"))