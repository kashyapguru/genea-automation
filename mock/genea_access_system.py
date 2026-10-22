"""
Mock Genea Access Control System
================================
A lightweight in-memory stand-in for Genea's access-control backend, so the
demo test suite is fully runnable WITHOUT access to Genea's real application,
credentials, or a test environment.

It models the core domain the real product exposes:
  - credentials (an access card / mobile key granted to a user at a door group)
  - provisioning (grant access), revoking (deactivate), and unlock attempts

In a real engagement these methods would be replaced by calls to Genea's
actual REST API, but the TEST DESIGN
and assertions would be identical — which is the point of this demo.
"""

from datetime import datetime
import uuid


class GeneaAccessSystem:
    def __init__(self):
        # credential_id -> credential record
        self._credentials = {}
        # simple audit log of access events
        self.events = []

    # ---- Provisioning -----------------------------------------------------
    def provision_credential(self, user, door_group, credential_type="card"):
        """Grant a user access to a door group. Returns the created credential."""
        if not user or not door_group:
            raise ValueError("user and door_group are required")
        if credential_type not in ("card", "mobile"):
            raise ValueError("credential_type must be 'card' or 'mobile'")

        cred_id = "CRED-" + uuid.uuid4().hex[:8].upper()
        record = {
            "credential_id": cred_id,
            "user": user,
            "door_group": door_group,
            "type": credential_type,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        self._credentials[cred_id] = record
        self.events.append(("provisioned", cred_id, user))
        return dict(record)

    # ---- Revoking ---------------------------------------------------------
    def revoke_credential(self, credential_id):
        """Deactivate a credential. Returns the updated record."""
        cred = self._credentials.get(credential_id)
        if cred is None:
            raise KeyError("credential not found")
        cred["status"] = "revoked"
        cred["revoked_at"] = datetime.now().isoformat()
        self.events.append(("revoked", credential_id, cred["user"]))
        return dict(cred)

    # ---- Querying ---------------------------------------------------------
    def get_credential(self, credential_id):
        cred = self._credentials.get(credential_id)
        return dict(cred) if cred else None

    def list_credentials(self, user=None):
        creds = list(self._credentials.values())
        if user:
            creds = [c for c in creds if c["user"] == user]
        return [dict(c) for c in creds]

    # ---- Unlock attempt (the real-world effect of a credential) -----------
    def attempt_unlock(self, credential_id, door_group):
        """
        Simulate presenting a credential at a door.
        Returns True if access granted, False if denied.
        Access is granted ONLY if the credential exists, is active, and matches
        the door group.
        """
        cred = self._credentials.get(credential_id)
        granted = bool(
            cred
            and cred["status"] == "active"
            and cred["door_group"] == door_group
        )
        self.events.append(("unlock_granted" if granted else "unlock_denied",
                             credential_id, door_group))
        return granted
