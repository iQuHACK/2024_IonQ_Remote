from typing import Any, Dict, Optional

from qbraid.api import QbraidSession
from qbraid.exceptions import QbraidError
from qbraid.transpiler import convert_to_package


class Server:
    """Server class containing the attack() and probe() methods for IonQ challenge."""

    def __init__(self, qbraid_session: Optional[QbraidSession] = None):
        """Initialize the server class with a QbraidSession object."""
        self._session = qbraid_session or QbraidSession()

    @property
    def session(self) -> QbraidSession:
        """Return the QbraidSession object."""
        return self._session

    @staticmethod
    def _verify_qasm_program(qasm: str) -> None:
        """Verify that the qasm program is valid."""
        try:
            _ = convert_to_package(qasm, "cirq")
        except QbraidError as err:
            raise ValueError("Invalid OpenQASM program.") from err

    def _post_request(
        self, action: str, vault_index: int, circuit: str
    ) -> Dict[str, Any]:
        """Send a request to a specified endpoint with given parameters."""
        self._verify_qasm_program(circuit)
        query = {"vaultIndex": vault_index, "openQasm": circuit}
        resp = self.session.post(f"/iquhack/ionq/{action}", json=query)
        return resp.json()

    def attack(self, vault_index: int, circuit: str) -> Dict[str, float]:
        """Returns score."""
        resp_data = self._post_request("attack", vault_index, circuit)
        score_keys = {"rawScore", "costFactor", "score"}
        score_dict = {k: resp_data[k] for k in score_keys if k in resp_data}
        return score_dict

    def probe(self, vault_index: int, circuit: str) -> Dict[str, float]:
        """Returns histogram data with keys in the big-endian decimal
        representation of measurement bit strings."""
        resp_data = self._post_request("probe", vault_index, circuit)
        return resp_data["histogram"]

    def state(self) -> Dict[str, Any]:
        """Returns user challenge metadata."""
        return self.session.get("/iquhack/ionq/state").json()

    def register(self, team_name: str) -> str:
        """Initialize session. Only needs to be done once."""
        resp = self.session.post(
            f"/iquhack/ionq/register", json={"teamName": team_name}
        ).json()
        message = resp["message"]
        for ln in message.split("\n"):
            print(ln.strip())
