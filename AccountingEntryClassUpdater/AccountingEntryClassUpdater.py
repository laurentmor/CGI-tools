import logging
import argparse
import xml.etree.ElementTree as ET
import time
from decorators import log_exceptions
# -*- coding: utf-8 -*-
#logger=None
class AccountingEntryClassUpdater:
    """
    This class processes an XML file containing SQL DEV EXPORT <ROWS> and generates SQL statements.
    It validates the XML structure, checks for required columns, and generates SQL SELECT/UPDATE statements
    based on the contents of the XML file.
    The generated SQL statements are written to a file named 'sql_statements.sql'.
    The class also includes logging functionality to track the progress and any errors encountered during processing.
    Attributes:
        logger (logging.Logger): Logger instance for logging messages.
        input_file (str): Path to the XML input file.
    Methods:
        run(): Main method to execute the updater logic.
        get_row_count(): Returns the number of rows in the XML file.
        validate_xml_structure(input_file): Validates the XML structure of the input file.
        validate_columns_exist(input_file, column_names): Checks if the required columns exist in the XML file.

    """
    def __init__(self, log_file='accounting_entry_updater.log', input_file='export.xml'):
       self.logger = logging.getLogger(self.__class__.__name__)
       self.logger.setLevel(logging.INFO)

       formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
       console_handler = logging.StreamHandler()
       console_handler.setFormatter(formatter)
       file_handler = logging.FileHandler(log_file)
       file_handler.setFormatter(formatter)
       self.logger.addHandler(console_handler)
       self.logger.addHandler(file_handler)
       self.input_file = input_file
       self.log_file = log_file
       self.logger.info("Initialized AccountingEntryClassUpdater")

    @log_exceptions({FileNotFoundError: "Input file not found", ET.ParseError: "Error parsing XML"}, raise_exception=True, logger=lambda self: self.logger)
    def run(self):
        start=time.time()
        self.logger.info("Starting AccountingEntryClassUpdater script...")
        self.logger.info(f"Input file: {self.input_file}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info("Validating XML structure...")

        if not self.validate_xml_structure(self.input_file):
            self.logger.error("Invalid XML structure.")
            return

        self.logger.info("XML structure validated successfully.")
        self.logger.info("Validating required columns...")
        self.validate_columns_exist(self.input_file, ["INSTRUMENT_ID", "SEQ_NUMS", "TYPE_"])
        self.logger.info("Required columns validated successfully.")
        self.logger.info("Getting row count...")
        row_count = self.get_row_count()
        self.logger.info(f"Found {row_count} rows in XML.")

        self.logger.info("Processing XML file...")
        tree = ET.parse(self.input_file)
        root = tree.getroot()
        code = ""
        result = []
        for row in root.findall("ROW"):
            # Extracting the columns and their values from the XML
            # Assuming each row has multiple columns with the tag "COLUMN"
            # and each column has a "NAME" attribute and text value or "" if text is empty
            # Example: <COLUMN NAME="INSTRUMENT_ID">12345</COLUMN>

            line = {col.attrib.get("NAME"): (col.text or "").strip() for col in row.findall("COLUMN")}

            result.append(line)
            instrument_ID = line.get("INSTRUMENT_ID")
            seqs = line.get("SEQ_NUMS")
            type_ = line.get("TYPE_")
            self.logger.info(f"writing SELECT/UPDATE statements for instrument_ID: {instrument_ID}, SEQ_NUMS: {seqs}, TYPE_: {type_}")
            elements = [v.strip() for v in seqs.split(",") if v.strip()]
            code += f"\n\n -- PROMPT *** PROCESSING INSTRUMENT_ID: {instrument_ID} SEQ_NUMS: {seqs} TYPE_: {type_} ***\n\n"

            # Check if SEQ_NUMS is empty
            if  len(elements) == 0:
                    self.logger.info(f"No SEQ_NUMS found for instrument_ID: {instrument_ID}")
                    block = f"""
    SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
    WHERE P_activity = (
        SELECT uoid FROM activity
        WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
        AND A_activity_type = '{type_}'
        AND SEQ_NUM_OF_ACTV_TY IS NULL
    ) AND A_OBJ_ACC_TYPE_CLS IS NULL;
    UPDATE accounting_entry SET A_OBJ_ACC_TYPE_CLS = 'n_cst_codeobj_chargetype'
    WHERE P_activity = (
        SELECT uoid FROM activity
        WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
        AND A_activity_type = '{type_}'
        AND SEQ_NUM_OF_ACTV_TY IS NULL
    ) AND A_OBJ_ACC_TYPE_CLS IS NULL;

    COMMIT;

    SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
    WHERE P_activity = (
        SELECT uoid FROM activity
        WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
        AND A_activity_type = '{type_}'
        AND SEQ_NUM_OF_ACTV_TY IS NULL
    ) AND A_OBJ_ACC_TYPE_CLS IS NOT NULL;

"""

            # Check if SEQ_NUMS is a single value
            if len(elements) == 1:
                    self.logger.info(f"Single SEQ_NUM found: {elements[0]}")
                    element = elements[0]
                    block = f"""
SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
WHERE P_activity = (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY = '{element}'
) AND A_OBJ_ACC_TYPE_CLS IS NULL;

UPDATE accounting_entry SET A_OBJ_ACC_TYPE_CLS = 'n_cst_codeobj_chargetype'
WHERE P_activity = (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY = '{element}'
) AND A_OBJ_ACC_TYPE_CLS IS NULL;

COMMIT;

SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
WHERE P_activity = (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY = '{element}'
) AND A_OBJ_ACC_TYPE_CLS IS NOT NULL;
"""
            # Check if SEQ_NUMS contains multiple values
            elif len(elements) > 1:
                    self.logger.info(f"Multiple SEQ_NUMS found: {elements}")
                    activities = ",".join(f"'{v}'" for v in elements)
                    block = f"""
SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
WHERE P_activity IN (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY IN ({activities})
) AND A_OBJ_ACC_TYPE_CLS IS NULL;

UPDATE accounting_entry SET A_OBJ_ACC_TYPE_CLS = 'n_cst_codeobj_chargetype'
WHERE P_activity IN (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY IN ({activities})
) AND A_OBJ_ACC_TYPE_CLS IS NULL;

COMMIT;


SELECT A_OBJ_ACC_TYPE_CLS, accounting_entry.* FROM accounting_entry
WHERE P_activity IN (
    SELECT uoid FROM activity
    WHERE P_instrument = (SELECT uoid FROM instrument WHERE instrument_id = '{instrument_ID}')
    AND A_activity_type = '{type_}'
    AND SEQ_NUM_OF_ACTV_TY IN ({activities})
) AND A_OBJ_ACC_TYPE_CLS IS NOT NULL;
"""
            code += block


            # Write the generated SQL code to a file
            with open("sql_statements.sql", "w") as sql_file:
                sql_file.write(code)

        self.logger.info("SQL statements successfully written.")


    @log_exceptions({Exception:"Error occurred while getting row count" }, raise_exception=True, logger=lambda self: self.logger)
    def get_row_count(self):
        """
        Returns the number of rows in the XML file.
        """
        return sum(1 for _, elem in ET.iterparse(self.input_file) if elem.tag == "ROW")

    @log_exceptions({Exception:"Error occurred while validating XML structure" }, raise_exception=True, logger=lambda self: self.logger)
    def validate_xml_structure(self, input_file):
           """Validates the XML structure of the input file.
           Returns True if the XML structure is valid, False otherwise.
           """
           return True if ET.parse(input_file) else False

    def validate_columns_exist(self, input_file, column_names):
        """
        Validates the presence of required columns in the XML file.

        """
        required = set(column_names)
        found = set()

        for _, elem in ET.iterparse(input_file):
            if elem.tag == "ROW":
                present = {col.attrib.get("NAME") for col in elem.findall("COLUMN")}
                found.update(required & present)
                if found == required:
                    return
        missing = required - found
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Update accounting entry classes from XML exports.")
    parser.add_argument('--log-file', type=str, default='accounting_entry_updater.log', help='Log file path.')
    parser.add_argument('input_file', type=str, help='Path to the XML input file.')

    args = parser.parse_args()
    updater = AccountingEntryClassUpdater(log_file=args.log_file, input_file=args.input_file)
    updater.run()

if __name__ == "__main__":
    main()
