"""Implementation of Blacklist store."""

from flask import current_app, Flask

from .utilities import must_be_initialized


class Blacklist:
    """Store of invalidated jti.

    Blacklist stores blacklisted jti in a `set` and provides lookup functionality
    to flask_praetorian that is very fast (As compared to a database lookup), but
    it also provides a method that persists the blacklisted jti to the database when
    the token is invalidated.  Further lookups for this blacklisted jti hit the set,
    not the database.

    It was written to be used with sqlalchemy, but as long as the required
    methods work as required, then it should work for your ORM.
    """

    def __init__(self, app=None, token_class=None) -> None:
        """Constructor."""
        self.store: set = None
        self.token_class = None
        self.initialized: bool = False
        if app is not None and token_class is not None:
            self.init_app(app, token_class)

    def __eq__(self, other) -> bool:
        """Evaluate equality."""
        if other.__class__.__name__ == 'Blacklist':
            if self.store == other.store:
                return True
        return False

    def __repr__(self):
        """Return `eval`-able string name."""
        return f'{self.__class__.__name__}()'

    def __str__(self):
        """Return descriptive string name."""
        if not self.store:
            store_items = 0
        else:
            store_items = len(self.store)
        return f'<{self.__class__.__name__} with {store_items} item(s)>'

    def init_app(self, app: Flask, token_class) -> None:
        """Deferred Initialization.

        :param app: Flask app
        :param token_class:  Database model class. Written with sqlalchemy
        in mind, but should work with any orm, as long as the required methods
        are present on the database model.
        Those methods are:

            `blacklist_jti - should persist jti to the database, takes one argument
                ex: token_class_model.blacklist_jti(jti) -> Any return value, but
                it should persist token to database

            `get_blacklisted` should return a list of `token` objects that have the
            'jti' attribute.
                ex: token_class.get_blacklisted() -> List[token] where
                `token['jti'] is not None`

        :return: None
        """
        if getattr(app, "extensions") is None:
            app.extensions = {}
        self.token_class = Blacklist._validate_token_class(token_class)
        try:
            self.store = self._load_store_from_database()
        except Exception:
            raise RuntimeError('Error: did you initialize Blacklist '
                               'after your ORM or forget to initialize the flask app?')
        self.initialized = True
        app.extensions["blacklist"] = self

    @classmethod
    def _validate_token_class(cls, token_class):
        """Validate token_class.

        Ensures that the token_class supplied has `blacklist_jti` and `get_blacklisted`
        methods

        :param token_class: ORM database model.
        :return: token_class
        :raises RuntimeError if token_class is missing required methods.
        """
        if getattr(token_class, "blacklist_jti") is None:
            raise RuntimeError(
                "token_class must have a blacklist_jti method that persists data to "
                "database"
            )
        if getattr(token_class, "get_blacklisted") is None:
            raise RuntimeError(
                "token_class must have a get_blacklisted method that returns a list "
                "of blacklisted tokens with attr `jti`"
            )
        return token_class

    def _load_store_from_database(self) -> set:
        """Load blacklisted tokens into store.

        Populates Blacklist.store with jti obtained from call to
        token_class.get_blacklisted.
        :return: `set`
        """
        store = set()
        with current_app.app_context():
            blacklisted = self.token_class.get_blacklisted()
        for token in blacklisted:
            jti = token["jti"]
            store.add(jti)
        return store

    @must_be_initialized
    def is_blacklisted(self, jti) -> bool:
        """Check for blacklisted tokens.

        :param jti: jti to be checked
        :return: boolean, if jti is in store and invalid
        :raises RuntimeError if Blacklist.initialized isn't True
        """
        return jti in self.store

    @must_be_initialized
    def blacklist_jti(self, jti) -> None:
        """Blacklist token.

        Adds jti to Blacklist.store as well as the token_store's associated database

        :param jti:
        :return: None
        :raises RuntimeError if Blacklist.initialized isn't True
        """
        self.store.add(jti)
        with current_app.app_context():
            self.token_class.blacklist_jti(jti)
