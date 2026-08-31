class FakeDocSnapshot:
    """Stand-in for a Firestore DocumentSnapshot."""

    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class FakeDocRef:
    """Stand-in for a Firestore DocumentReference, backed by a shared dict."""

    def __init__(self, store, doc_id):
        self._store = store
        self._id = doc_id

    def get(self):
        return FakeDocSnapshot(self._id, self._store.get(self._id))

    def set(self, data):
        self._store[self._id] = dict(data)

    def update(self, data):
        self._store[self._id].update(data)


class FakeCollection:
    """Stand-in for a Firestore CollectionReference, backed by a shared dict."""

    def __init__(self, store):
        self._store = store
        self._limit = None

    def document(self, doc_id):
        return FakeDocRef(self._store, doc_id)

    def limit(self, n):
        self._limit = n
        return self

    def stream(self):
        ids = list(self._store.keys())
        if self._limit is not None:
            ids = ids[: self._limit]
        return [FakeDocSnapshot(doc_id, self._store[doc_id]) for doc_id in ids]


class FakeFirestore:
    """Stand-in for a Firestore Client, in-memory, single 'users' collection.

    Pass a dict of {uid: profile_dict} to seed existing users.
    """

    def __init__(self, users=None):
        self.users = users or {}

    def collection(self, name):
        assert name == "users"
        return FakeCollection(self.users)


class FakeChatGraph:
    """
    Stand-in for the compiled LangGraph workflow (graph.workflow.app).
    Configure `.answer`, `.category`, or `.raise_exc` before making a
    request to control the outcome of POST /chat/.
    """

    def __init__(self, answer="Mocked AI reply", category="ifrs", raise_exc=None):
        self.answer = answer
        self.category = category
        self.raise_exc = raise_exc
        self.last_invoke_state = None

    def invoke(self, state):
        self.last_invoke_state = state
        if self.raise_exc:
            raise self.raise_exc
        result = {"answer": self.answer}
        if self.category is not None:
            result["category"] = self.category
        return result
