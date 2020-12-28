from dataclasses import dataclass


@dataclass
class ContractItem:
    """The Item of contract

    Contains info about each position in contract

    Args
        is_included: bool
            true if the contract issuer has submitted this item with the contract, false if the isser is asking for this item in the contract
        is_singleton: bool
        quantity: int
            Number of items in the stack
        raw_quantity: int
            -1 indicates that the item is a singleton (non-stackable). If the item happens to be a Blueprint, -1 is an Original and -2 is a Blueprint Copy
        record_id: int
            Unique ID for the item
        type_id: int
            Type ID for item
    """
    is_included: bool
    is_singleton: bool
    quantity: int
    raw_quantity: int
    record_id: int
    type_id: int
