from db_service.db_initialize import DBInitializer
from db_service.models import DBRequestState, DBRequestType
from db_service.session_manager import SessionManager
from db_service.tests.db_testcase import DBTestCase


class DBInitializationTestCase(DBTestCase):

    def setUp(self):
        super().setUp()
        self.initializer = DBInitializer(SessionManager(db_engine=self.engine))

    def test_db_is_initialized_with_db_states_and_types(self):
        # Given
        types_pre_init = self.session.query(DBRequestType).all()
        states_pre_init = self.session.query(DBRequestState).all()

        # When
        self.initializer.initialize()

        types_post_init = self.session.query(DBRequestType).all()
        states_post_init = self.session.query(DBRequestState).all()

        # Then
        self.assertEqual(0, len(types_pre_init))
        self.assertEqual(0, len(states_pre_init))
        self.assertEqual(6, len(types_post_init))
        self.assertEqual(2, len(states_post_init))

    def test_db_is_initialized_only_once(self):
        # Given / When
        self.initializer.initialize()
        types_post_init_1 = self.session.query(DBRequestType).all()
        states_post_init_1 = self.session.query(DBRequestState).all()

        self.initializer.initialize()
        types_post_init_2 = self.session.query(DBRequestType).all()
        states_post_init_2 = self.session.query(DBRequestState).all()

        # Then
        self.assertListEqual(types_post_init_1, types_post_init_2)
        self.assertListEqual(states_post_init_1, states_post_init_2)
