
# todo test rename
# todo test rename invalid name
# todo test rename invalid name already exist
# todo test me

# todo test update user
# todo test get user friend field


class Test01_GetUsers(UnitTest):

    def test_001_get_user(self):
        self.assertResponse(get_user(), 200)
