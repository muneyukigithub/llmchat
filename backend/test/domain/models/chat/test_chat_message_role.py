from domain.models.chat.chat_message_role import Role
import pytest
from domain.exceptions import InvalidValueError
class TestChatMessageRoleInit:      
    def test_init_with_user(self):
        role = Role.USER
        assert role.value == "user"

    def test_init_with_model(self):
        role = Role.MODEL
        assert role.value == "model"

    def test_init_with_invalid_role(self):
        with pytest.raises(ValueError):
            Role("invalid_role")

    def test_init_string(self):
        role = Role("user")
        assert Role.USER == role

    def test_equality(self):
        role1 = Role.USER
        role2 = Role.USER
        role3 = Role.MODEL
        assert role1 == role2
        assert role1 != role3
        assert role2 != role3
   