# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Laurent Morissette

from enum import StrEnum


class ProductType(StrEnum):
    DLC = "DLC"
    SLC = "SLC"
    CAR = "CAR"
    RMB = "RMB"
    DBA = "DBA"
    CBA = "CBA"
    RBA = "RBA"
    DFP = "DFP"
    ADV = "ADV"
    LOI = "LOI"
    DCO = "DCO"
    DIR = "DIR"
    TAC = "TAC"
    GUA = "GUA"
    PBD = "PBD"
    PBS = "PBS"
    SBS = "SBS"
    FIN = "FIN"
    ATP = "ATP"
    OAP = "OAP"
    RPM = "RPM"
    SRM = "SRM"
    BIL = "BIL"  # Added 01 march 2026


class InstrumentClass(StrEnum):
    DOCUMENTARY_LC = "documentary_lc"
    STANDBY_LC = "standby_lc"
    CARGO_RELEASE = "cargo_release"
    REIMBURSEMENT = "reimbursement"
    DOCUMENTARY_BA = "documentary_ba_instrument"
    CLEAN_BA = "clean_ba_instrument"
    REFINANCE_BA = "refinance_ba_instrument"
    DEFERRED_PAYMENT = "deferred_payment_instrument"
    ADVANCE = "advance_instrument"
    LETTER_OF_INDEMNITY = "letter_of_idemnity"
    DOCUMENTARY_COLLECTION = "documentary_collection_instrument"
    DIRECT_SEND_COLLECTION = "direct_send_collection_instrument"
    TRADE_ACCEPT = "trade_accept_instrument"
    GUARANTEE = "guarantee"
    PARTICIPATION_DLC = "participation_bought_documentary_lc"
    PARTICIPATION_SLC = "participation_bought_standby_lc"
    SYNDICATION_DLC = "syndication_bought_documentary_lc"
    FINANCE = "finance_instrument"
    APPROVAL_TO_PAY = "approval_to_pay_instrument"
    OPEN_ACCOUNT_PAYMENT = "open_account_payment"
    RPM = "receivables_payables_management"
    SRM = "selective_receivable_management"
    BIL = "billing_instrument"  # Added 01 march 2026


PRODUCT_TO_INSTRUMENT = {
    ProductType.DLC: InstrumentClass.DOCUMENTARY_LC,
    ProductType.SLC: InstrumentClass.STANDBY_LC,
    ProductType.CAR: InstrumentClass.CARGO_RELEASE,
    ProductType.RMB: InstrumentClass.REIMBURSEMENT,
    ProductType.DBA: InstrumentClass.DOCUMENTARY_BA,
    ProductType.CBA: InstrumentClass.CLEAN_BA,
    ProductType.RBA: InstrumentClass.REFINANCE_BA,
    ProductType.DFP: InstrumentClass.DEFERRED_PAYMENT,
    ProductType.ADV: InstrumentClass.ADVANCE,
    ProductType.LOI: InstrumentClass.LETTER_OF_INDEMNITY,
    ProductType.DCO: InstrumentClass.DOCUMENTARY_COLLECTION,
    ProductType.DIR: InstrumentClass.DIRECT_SEND_COLLECTION,
    ProductType.TAC: InstrumentClass.TRADE_ACCEPT,
    ProductType.GUA: InstrumentClass.GUARANTEE,
    ProductType.PBD: InstrumentClass.PARTICIPATION_DLC,
    ProductType.PBS: InstrumentClass.PARTICIPATION_SLC,
    ProductType.SBS: InstrumentClass.SYNDICATION_DLC,
    ProductType.FIN: InstrumentClass.FINANCE,
    ProductType.ATP: InstrumentClass.APPROVAL_TO_PAY,
    ProductType.OAP: InstrumentClass.OPEN_ACCOUNT_PAYMENT,
    ProductType.RPM: InstrumentClass.RPM,
    ProductType.SRM: InstrumentClass.SRM,
    ProductType.BIL: InstrumentClass.BIL,  # Added March 1 2026
}


def resolve_class(type_: str) -> InstrumentClass:
    try:
        product = ProductType(type_.strip().upper())
        return PRODUCT_TO_INSTRUMENT[product]
    except KeyError:
        raise ValueError(f"No instrument mapping for product type: {type_}")
    except ValueError:
        raise ValueError(f"Invalid product type: {type_}")
