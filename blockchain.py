"""
blockchain.py - Educational Blockchain Simulation for Fake Product Identification

This module implements a lightweight, transparent SHA-256 blockchain ledger
for storing and verifying product registration records.
Each block represents a cryptographic receipt of a registered product.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


class Block:
    """Represents a single block in the educational blockchain."""

    def __init__(
        self,
        index: int,
        timestamp: str,
        product_id: str,
        data: Dict[str, Any],
        previous_hash: str,
        nonce: int = 0,
        block_hash: Optional[str] = None,
    ):
        self.index = index
        self.timestamp = timestamp
        self.product_id = product_id
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = block_hash or ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to a serializable dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "product_id": self.product_id,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Block":
        """Reconstruct a Block instance from dictionary representation."""
        data_field = d.get("data", {})
        if isinstance(data_field, str):
            try:
                data_field = json.loads(data_field)
            except Exception:
                data_field = {"raw": data_field}

        return cls(
            index=int(d["index"]),
            timestamp=str(d["timestamp"]),
            product_id=str(d["product_id"]),
            data=data_field,
            previous_hash=str(d["previous_hash"]),
            nonce=int(d.get("nonce", 0)),
            block_hash=str(d.get("hash", "")),
        )


class Blockchain:
    """
    Educational Blockchain implementation featuring SHA-256 cryptographic hashing,
    Proof-of-Work (PoW) simulation, chain integrity validation, and tamper detection.
    """

    def __init__(self, difficulty: int = 2):
        self.difficulty = difficulty  # Target difficulty (number of leading zeros)
        self.chain: List[Block] = []

    @staticmethod
    def compute_data_hash(data: Dict[str, Any]) -> str:
        """Calculate SHA-256 fingerprint for product metadata."""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def calculate_hash(
        self,
        index: int,
        timestamp: str,
        product_id: str,
        data: Dict[str, Any],
        previous_hash: str,
        nonce: int,
    ) -> str:
        """Calculate SHA-256 block hash based on block header and payload."""
        data_string = json.dumps(data, sort_keys=True)
        raw = f"{index}{timestamp}{product_id}{data_string}{previous_hash}{nonce}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def create_genesis_block(self) -> Block:
        """Create and mine the foundational Genesis Block."""
        timestamp = datetime.now(timezone.utc).isoformat()
        genesis_data = {
            "title": "Genesis Block",
            "message": "Origin block of the Fake Product Identification Blockchain Prototype",
            "protocol": "SHA-256 PoW Educational Simulation",
        }
        genesis_block = self.mine_block(
            index=0,
            timestamp=timestamp,
            product_id="GENESIS",
            data=genesis_data,
            previous_hash="0" * 64,
        )
        self.chain = [genesis_block]
        return genesis_block

    def get_latest_block(self) -> Optional[Block]:
        """Return the most recently added block in the chain."""
        return self.chain[-1] if self.chain else None

    def mine_block(
        self,
        index: int,
        timestamp: str,
        product_id: str,
        data: Dict[str, Any],
        previous_hash: str,
    ) -> Block:
        """
        Mine a new block using proof-of-work: increment nonce until
        the hash satisfies the difficulty criteria (e.g. starts with '00').
        """
        nonce = 0
        target_prefix = "0" * self.difficulty

        while True:
            current_hash = self.calculate_hash(
                index, timestamp, product_id, data, previous_hash, nonce
            )
            if current_hash.startswith(target_prefix):
                block = Block(
                    index=index,
                    timestamp=timestamp,
                    product_id=product_id,
                    data=data,
                    previous_hash=previous_hash,
                    nonce=nonce,
                    block_hash=current_hash,
                )
                return block
            nonce += 1

    def add_block(self, product_id: str, product_data: Dict[str, Any]) -> Block:
        """Add a new product record as a mined block to the blockchain."""
        if not self.chain:
            self.create_genesis_block()

        latest_block = self.get_latest_block()
        new_index = latest_block.index + 1 if latest_block else 1
        previous_hash = latest_block.hash if latest_block else "0" * 64
        timestamp = datetime.now(timezone.utc).isoformat()

        # Attach computed data hash for cryptographic integrity verification
        payload = dict(product_data)
        payload["data_hash"] = self.compute_data_hash(product_data)

        mined_block = self.mine_block(
            index=new_index,
            timestamp=timestamp,
            product_id=product_id,
            data=payload,
            previous_hash=previous_hash,
        )
        self.chain.append(mined_block)
        return mined_block

    def validate_chain(self) -> Tuple[bool, str, Optional[int]]:
        """
        Verify the integrity of the entire blockchain:
        1. Ensure block hashes match calculated hashes.
        2. Ensure previous_hash pointers match previous block hashes.
        3. Ensure difficulty target is satisfied.
        Returns: (is_valid, message, broken_block_index)
        """
        if not self.chain:
            return False, "Blockchain is empty.", None

        target_prefix = "0" * self.difficulty

        for i, current_block in enumerate(self.chain):
            # Recalculate hash
            expected_hash = self.calculate_hash(
                current_block.index,
                current_block.timestamp,
                current_block.product_id,
                current_block.data,
                current_block.previous_hash,
                current_block.nonce,
            )

            # Check hash consistency
            if current_block.hash != expected_hash:
                return (
                    False,
                    f"Block #{current_block.index} hash mismatch. Computed: {expected_hash[:16]}... Stored: {current_block.hash[:16]}...",
                    current_block.index,
                )

            # Check proof of work
            if not current_block.hash.startswith(target_prefix):
                return (
                    False,
                    f"Block #{current_block.index} does not satisfy difficulty requirement ({self.difficulty} zeros).",
                    current_block.index,
                )

            # Check pointer to previous block
            if i > 0:
                previous_block = self.chain[i - 1]
                if current_block.previous_hash != previous_block.hash:
                    return (
                        False,
                        f"Block #{current_block.index} previous_hash does not match Block #{previous_block.index} hash.",
                        current_block.index,
                    )

        return True, "Blockchain integrity verified. All blocks valid.", None

    def get_block_by_product_id(self, product_id: str) -> Optional[Block]:
        """Find the block corresponding to a given product ID."""
        for block in self.chain:
            if block.product_id.strip().lower() == product_id.strip().lower():
                return block
        return None

    def get_block_by_verification_code(self, code: str) -> Optional[Block]:
        """Find the block matching a specific verification code."""
        code_cleaned = code.strip().upper()
        for block in self.chain:
            if isinstance(block.data, dict):
                stored_code = block.data.get("verification_code", "").strip().upper()
                if stored_code == code_cleaned:
                    return block
        return None

    def verify_product_record(
        self, product_id: str, db_product_data: Dict[str, Any]
    ) -> Tuple[str, str, Optional[Dict[str, Any]]]:
        """
        Verify product against blockchain:
        Returns:
            status: 'VERIFIED' | 'INTEGRITY_FAILED' | 'NOT_IN_BLOCKCHAIN'
            message: User-friendly explanation
            block_info: Metadata dictionary for display
        """
        # Step 1: Check entire chain integrity first
        chain_valid, chain_msg, broken_idx = self.validate_chain()
        if not chain_valid:
            return (
                "INTEGRITY_FAILED",
                f"Global Blockchain validation failed at Block #{broken_idx}: {chain_msg}",
                None,
            )

        # Step 2: Locate block for this product
        block = self.get_block_by_product_id(product_id)
        if not block:
            return (
                "NOT_IN_BLOCKCHAIN",
                f"Product ID '{product_id}' exists in database but has no corresponding block in the blockchain ledger.",
                None,
            )

        # Step 3: Check cryptographic payload match
        stored_data = block.data
        stored_hash = stored_data.get("data_hash")
        computed_current_hash = self.compute_data_hash(db_product_data)

        if stored_hash and stored_hash != computed_current_hash:
            return (
                "INTEGRITY_FAILED",
                "Product record integrity check failed: stored database details do not match the cryptographic payload on the blockchain.",
                block.to_dict(),
            )

        return (
            "VERIFIED",
            "Blockchain record verified successfully. Cryptographic hash matches distributed block header.",
            block.to_dict(),
        )

    def tamper_block_for_demo(self, product_id: str) -> Tuple[bool, str]:
        """
        Educational demonstration tool:
        Intentionally modifies a block's data without re-mining its hash,
        simulating an unauthorized malicious edit so that validate_chain() fails.
        """
        block = self.get_block_by_product_id(product_id)
        if not block:
            return False, f"Product ID '{product_id}' not found in blockchain."

        # Mutate block data while storing clean original for repair
        if isinstance(block.data, dict):
            if "_original_data" not in block.data:
                block.data["_original_data"] = dict(block.data)
            block.data["TAMPERED_BY_ATTACKER"] = True
            block.data["manufacturer"] = "MALICIOUS_COUNTERFEIT_CORP"
            block.data["data_hash"] = "00000000tamperedfakehash00000000"
        return True, f"Block #{block.index} for product '{product_id}' tampered successfully for demonstration."

    def repair_chain(self) -> Tuple[bool, str]:
        """
        Educational helper: Re-mines all invalid blocks in sequence
        to restore a clean valid chain after a tamper demonstration.
        """
        if not self.chain:
            return False, "Chain is empty."

        for i, block in enumerate(self.chain):
            if i == 0:
                block.previous_hash = "0" * 64
            else:
                block.previous_hash = self.chain[i - 1].hash

            # Restore original clean payload if corrupted during demo
            if isinstance(block.data, dict):
                if "_original_data" in block.data:
                    orig = block.data.pop("_original_data")
                    block.data = orig
                block.data.pop("TAMPERED_BY_ATTACKER", None)
                data_copy = dict(block.data)
                data_copy.pop("data_hash", None)
                block.data["data_hash"] = self.compute_data_hash(data_copy)

            # Re-mine
            mined = self.mine_block(
                block.index,
                block.timestamp,
                block.product_id,
                block.data,
                block.previous_hash,
            )
            block.nonce = mined.nonce
            block.hash = mined.hash

        return True, "Blockchain successfully re-mined and repaired."

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Export all blocks as list of dictionaries."""
        return [block.to_dict() for block in self.chain]

    def load_from_dict_list(self, blocks_data: List[Dict[str, Any]]) -> None:
        """Load and sort blocks from stored list."""
        self.chain = [Block.from_dict(b) for b in blocks_data]
        self.chain.sort(key=lambda b: b.index)
