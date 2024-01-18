import tabula
import os
import sys
import json

def get_data_for_page(page_data):
 output = []
 for items in page_data:
  new_entry = []
  for i in items:
   if len(i["text"]) > 0:
    new_entry += i["text"]
  output += new_entry
 return output




try:
 input_file_name = sys.argv[1]
except IndexError:
 input_file_name = input("Input file name: ")

try:
 input_file_type = sys.argv[2]
except IndexError:
 print("File type not provided in args; using default file type: pdf.")
 input_file_type = "pdf"

advance_payments_source_file = ""
try:
 advance_payments_source_file = sys.argv[3] + ".json"
except IndexError:
 print("JSON file for advance payments not provided.")
# advance_payments_source_file = input_file_name + "-input-data.json"

if len(advance_payments_source_file) > 0:
 try:
  print("Loading JSON source file: " + advance_payments_source_file)
  with open(advance_payments_source_file, "r") as source_file:
   print("JSON file opened; loading JSON data...")
   advance_payments_json_data = json.load(source_file)
 except AttributeError:
  print("JSON loading operation failed.")
  advance_payments_source_file = ""

input_file = input_file_name + "." + input_file_type
print("Opening file " + input_file + " for retrieving data...")

tables = tabula.read_pdf(input_file, pages="all", output_format="json")

tables_count = len(tables)
#print("Available tables: " + str(tables_count))

print("File " + input_file_name + " opened.")
print("Processing contents of the file.")
print("Please wait...")

processed_entries = []

global i
i = 0
while i < tables_count:
 print("...")
 table_contents = tables[i]["data"]
 trimmed_table_data = {}
 j = 0
 for data_items in table_contents:
  entry_value = ""
  for e in data_items:
   text = e["text"]
   if len(text) > 0:
    entry_value += text + "|"
  trimmed_entry = entry_value.replace("|", " ")

  #print("New entry: " + trimmed_entry)
  trimmed_table_data[j] = trimmed_entry
  j = j + 1

 #print("Trimmed data length: " + str(len(trimmed_table_data)) + "\n")
 #print("Trimmed data: " + str(trimmed_table_data))
 
 processed_entries.append(trimmed_table_data)
 i = i + 1

#print("Content length: " + str(len(processed_entries)))
#print(processed_entries)
#print()

print("Processing complete.")
print()
print()
print()

dates = []
payments = []
debts = []
capitals = []
final_period_debts = []
assurances = []

print("Formatting data...")
formatted_data = []
for entry in processed_entries:
 i = 0
 print("...")
 while entry.get(i) is not None:
  #print("Splitting entry: " + entry.get(i))
  split_string = entry[i].split()
  if (len(split_string) != 6):
   i = i + 1
   continue
  #print("New split: " + str(split_string))

  dates.append(split_string[0])
  payments.append(split_string[1])
  debts.append(split_string[2])
  capitals.append(split_string[3])
  final_period_debts.append(split_string[4])
  assurances.append(split_string[5])
  i = i + 1
print("Validate data...")
is_data_valid = len(dates) == len(payments) == len(debts) == len(capitals) == len(final_period_debts) == len(assurances)
validation_state = "Invalid"
if is_data_valid:
 validation_state = "Valid"
print("Data validation complete; data: " + validation_state)
print()
print("Formatting complete.")

print()
print()
print("Setting up interface. Please wait.")
print()
should_run_script = True
print("All setup complete.")
print("Enjoy debt-sim!")
print()
print()
print()

global covered_debt
global debt_saved
global dates_copy
global payments_copy
global debts_copy
global capitals_copy
global final_period_debts_copy
global new_end_date
covered_debt = 0
debt_saved = 0
new_end_date = ""
dates_copy = dates.copy()
payments_copy = payments.copy()
debts_copy = debts.copy()
capitals_copy = capitals.copy()
final_period_debts_copy = final_period_debts.copy()

def compute_simulation_for_payment_of (payment, is_advance_payment):
 global i
 i = 0
 global covered_debt
 covered_debt = 0
 while covered_debt < payment:
  new_sum = covered_debt + float(capitals_copy[i])
  if new_sum > payment:
   break

  covered_debt = new_sum
  i = i + 1

 j = 0
 global debt_saved
 global new_end_date
 debt_saved = 0
 if is_advance_payment == True:
  while j < i:
   debt_saved += float(debts_copy[j])
   j = j + 1
   #global new_end_date
   new_end_date = dates_copy[len(dates_copy) - 1 - j]
 else:
  j = 1
  #global new_end_date
  new_end_date = dates_copy[len(dates_copy) - 1]

 while j != 0:
  if is_advance_payment == True:
   dates_copy.pop(len(dates_copy) - 1)
  else:
   dates_copy.pop(0)
  
  final_period_debts_copy.pop(0)
  debts_copy.pop(0)
  payments_copy.pop(0)
  capitals_copy.pop(0)
  j = j - 1

while should_run_script:
 print("#####################################################################################")
 print("Next payment date: " + dates[0])
 
 i = 0
 print("Upcoming payments:")
 print("Date		Payment		Debt value	Capital		Remaining capital")
 while i < len(dates_copy):
  print(dates_copy[i] + "	" + payments_copy[i] + "		" + debts_copy[i] + "		" + capitals_copy[i] + "		" + final_period_debts_copy[i])
  i = i + 1
 
 print()
 print()
 print("[ 1 ] Simulate advance payment.")
 if len(advance_payments_source_file) != 0:
  print("[ 2 ] Use JSON file as source.")
  print("[ 3 ] Simulate next payment.")
  print("[ 4 ] Exit simulator.")
 else:
  print("[ 2 ] Simulate next payment.")
  print("[ 3 ] Exit simulation.")
 print()
 user_option = int(input("Select option to continue:"))
 if user_option == 1:
  advance_payment = float(input("Enter advance payment value:"))
  print("Calculating simulation...")
  i = 0
  compute_simulation_for_payment_of(advance_payment, True)
 elif user_option == 2 and len(advance_payments_source_file) != 0:
  print("Processing simulation based on JSON file: " + advance_payments_source_file)
  i = 0
  for entry in advance_payments_json_data["data"]:
   if entry["value"] > 0:
     compute_simulation_for_payment_of(entry[value])
     print("Computing...")
  "Simulation complete."
 elif user_option == 2:
  print("Processing next monthly payment...")
  i = 0
  compute_simulation_for_payment_of(float(capitals_copy[0]), False)
 elif user_option == 3:
  print("Goodbye!")
  should_run_script = False
  break

 print()
 month_string = " month"
 if i > 1:
  month_string += "s"
 print("Payment would cover: " + str(i) + month_string)
 print("Covered capital: " + str(covered_debt))
 print("Generated debt savings: " + str(debt_saved))
 print("New end date: " + new_end_date)
