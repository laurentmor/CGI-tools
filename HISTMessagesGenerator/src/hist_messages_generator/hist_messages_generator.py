# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

"""
HISTMessagesGenerator

This module generates HIST interface messages from an XML file exported
from SQL Developer (<ROWS> format).

Author: Laurent Morissette
"""

import argparse
import logging
import time
import xml.etree.ElementTree as ET
from enum import IntEnum

from rich.logging import RichHandler

from .logging_decorators import log_exceptions
from .product_class_resolver import resolve_class
from .version import __version__


class InstrumentIndex(IntEnum):
    CLASS = 0
    PARTY_TYPE = 1


class HISTMessagesGenerator:
    """
    Processes XML and generates SQL HIST messages.
    """

    # ==========================
    # LOGGER (option 2: shared for all instances)
    # ==========================

    logger = logging.getLogger(f"HISTMessagesGenerator - {__name__}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    def __init__(
        self,
        log_file="HISTMessagesGenerator.log",
        input_file="export.xml",
        customer="",
        bank="",
        enable_file_logging=True,
    ):

        self.input_file = input_file
        self.log_file = log_file
        self.customer = customer
        self.bank = bank

        if enable_file_logging:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
            )
            HISTMessagesGenerator.logger.addHandler(file_handler)

        HISTMessagesGenerator.logger.info("Initialized HISTMessagesGenerator")

    # ==========================
    # MAIN EXECUTION
    # ==========================
    @log_exceptions(
        {FileNotFoundError: "Input file not found", ET.ParseError: "Error parsing XML"},
        raise_exception=True,
        logger=lambda self: HISTMessagesGenerator.logger,
    )
    def run(self):
        start = time.time()
        HISTMessagesGenerator.logger.info("Starting HISTMessagesGenerator script...")
        HISTMessagesGenerator.logger.info(f"Input file: {self.input_file}")
        HISTMessagesGenerator.logger.info(f"Customer: {self.customer}")
        HISTMessagesGenerator.logger.info(f"Bank: {self.bank}")

        HISTMessagesGenerator.logger.info("Validating XML structure...")
        if not self.validate_xml_structure(self.input_file):
            HISTMessagesGenerator.logger.error("Invalid XML structure.")
            return

        HISTMessagesGenerator.logger.info("XML structure validated successfully.")
        HISTMessagesGenerator.logger.info("Validating required columns...")
        self.validate_columns_exist(
            self.input_file, ["INSTRUMENT_ID", "TYPE_", "CUSTOMER_PARTY_TYPE"]
        )
        HISTMessagesGenerator.logger.info("Required columns validated successfully.")
        HISTMessagesGenerator.logger.info("Getting row count...")
        row_count = self.get_row_count()
        HISTMessagesGenerator.logger.info(f"Found {row_count} rows in XML.")

        HISTMessagesGenerator.logger.info("Processing XML file...")
        tree = ET.parse(self.input_file)
        root = tree.getroot()
        instruments = self.build_instruments_dictionary(root)
        effective_count = len(instruments)

        code = f"-- HIST for customer {self.customer} - {effective_count} Messages "
        select = """
select * from outgoing_intrfc_e where A_INTRFC_EVENT_TY= 'HIST' and A_INSTRUMENT in ( select UOID from instrument where instrument_id in ( """

        in_content = ",".join(f"'{ID}'" for ID in instruments if ID)
        select += f"{in_content} ));\n\n"
        code += select

        HISTMessagesGenerator.logger.info(
            f"*** Generating Inserts {self.customer} - {effective_count} Messages ***"
        )
        for instrument_ID, instrument_attributes in instruments.items():
            current_class = instrument_attributes[InstrumentIndex.CLASS].value
            current_party_type = instrument_attributes[InstrumentIndex.PARTY_TYPE]
            HISTMessagesGenerator.logger.info(
                f"ID -> {instrument_ID} Attributes -> (Class {current_class}, PARTY_TYPE {current_party_type})"
            )
            code += f"""INSERT INTO outgoing_intrfc_e ( UOID, DATE_BUSINESS, DATE_CREATED, PRIORITY, PROCESS_PARAMETERS, STATUS, TIME_CREATED, A_INSTRUMENT, A_CUSTOMER , A_INTRFC_EVENT_TY, A_OPER_BK_ORG, A_WORKER, A_CLIENT_BANK, MSG_CONFIRM_STATUS, DATETIME_SCHEDULED )
values (generate_uoid(), TO_DATE(TO_CHAR(SYSDATE, 'DD-MON-YYYY')), TO_DATE(TO_CHAR(SYSDATE, 'DD-MON-YYYY')), '1',
'|instrument_uoid ='|| (select UOID from instrument where instrument_id = '{instrument_ID}') ||'|instrument_id = {instrument_ID}|customer_id = {self.customer}|instrument_class = {current_class}|party_type = {current_party_type}|activity_uoid = |DestinationId = TPL',
'S', SYSDATE,
(select UOID from instrument where instrument_id = '{instrument_ID}'),
(select UOID from customer where customer_id = '{self.customer}'),
'HIST',
(select A_OPER_BK_ORG_ORIG from instrument where instrument_id = '{instrument_ID}'),
(select uoid from worker where worker_id ='ASYAGT01'),
'{self.bank}','S',SYSDATE);\n\n"""

        code += "commit;\n\n"
        code += select
        with open("sql_statements.sql", "w") as sql_file:
            sql_file.write(code)

        HISTMessagesGenerator.logger.info("SQL statements successfully written.")
        HISTMessagesGenerator.logger.info(
            f"Total execution time: {time.time() - start:.2f} seconds"
        )

    # ==========================
    # BUILD INSTRUMENT DICTIONARY
    # ==========================
    def build_instruments_dictionary(self, xml):
        built_dict = dict()
        # dup_count=0
        for row in xml.findall("ROW"):
            line = {
                col.attrib.get("NAME"): (col.text or "").strip() for col in row.findall("COLUMN")
            }
            instrument_ID = line.get("INSTRUMENT_ID")
            instrument_CLASS = line.get("TYPE_")
            customer_party_type = line.get("CUSTOMER_PARTY_TYPE")

            if instrument_ID:
                if instrument_ID not in built_dict:
                    built_dict[instrument_ID] = (
                        resolve_class(instrument_CLASS),
                        customer_party_type,
                    )
                else:
                    HISTMessagesGenerator.logger.warning(
                        f"Duplicate instrument {instrument_ID} detected. Ignoring additional party_type {customer_party_type}"
                    )

        return built_dict

    # ==========================
    # VALIDATION METHODS
    # ==========================
    @log_exceptions(
        {Exception: "Error occurred while getting row count"},
        raise_exception=True,
        logger=lambda self: HISTMessagesGenerator.logger,
    )
    def get_row_count(self):
        return sum(1 for _, elem in ET.iterparse(self.input_file) if elem.tag == "ROW")

    @log_exceptions(
        {Exception: "Error occurred while validating XML structure"},
        raise_exception=True,
        logger=lambda self: HISTMessagesGenerator.logger,
    )
    def validate_xml_structure(self, input_file):
        return True if ET.parse(input_file) else False

    def validate_columns_exist(self, input_file, column_names):
        """
        Validates the presence of required columns in the XML file.
        """
        required = set(column_names)
        found = set()

        # Open the file explicitly so Windows does not lock it after parsing
        with open(input_file, "rb") as f:  # open in binary mode for ET.iterparse
            for _, elem in ET.iterparse(f):
                if elem.tag == "ROW":
                    present = {col.attrib.get("NAME") for col in elem.findall("COLUMN")}
                    found.update(required & present)
                    if found == required:
                        return
        missing = required - found
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description="Generate Hist Messages rows from XML exports.")
    parser.add_argument(
        "--log-file", type=str, default="HISTMessagesGenerator.log", help="Log file path."
    )
    parser.add_argument("input_file", type=str, help="Path to the XML input file.")
    parser.add_argument("customer", type=str, help="Customer ID")
    parser.add_argument("bank", type=str, help="Bank")
    parser.add_argument(
        "--version", action="version", version=f"HISTMessagesGenerator {__version__}"
    )

    args = parser.parse_args()
    updater = HISTMessagesGenerator(
        log_file=args.log_file, input_file=args.input_file, customer=args.customer, bank=args.bank
    )
    updater.run()


if __name__ == "__main__":
    main()
