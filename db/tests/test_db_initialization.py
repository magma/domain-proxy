from db.models import DBRequestType, DBRequestState
from db.tests.db_testcase import DBTestCase


class DBInitializationTestCase(DBTestCase):

    def test_db_is_initialized_with_db_states_and_types(self):
        # Given
        types_pre_init = self.session.query(DBRequestType).all()
        states_pre_init = self.session.query(DBRequestState).all()

        # When
        self.db.initialize()

        types_post_init = self.session.query(DBRequestType).all()
        states_post_init = self.session.query(DBRequestState).all()

        # Then
        self.assertEqual(0, len(types_pre_init))
        self.assertEqual(0, len(states_pre_init))
        self.assertEqual(6, len(types_post_init))
        self.assertEqual(2, len(states_post_init))

    def test_db_is_initialized_only_once(self):
        # Given / When
        self.db.initialize()
        types_post_init_1 = self.session.query(DBRequestType).all()
        states_post_init_1 = self.session.query(DBRequestState).all()

        self.db.initialize()
        types_post_init_2 = self.session.query(DBRequestType).all()
        states_post_init_2 = self.session.query(DBRequestState).all()

        # Then
        self.assertListEqual(types_post_init_1, types_post_init_2)
        self.assertListEqual(states_post_init_1, states_post_init_2)


