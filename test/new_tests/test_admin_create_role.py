# -*- coding: utf-8 -*-

import pytest
import time
from .test_base_class import TestBaseClass
from aerospike import exception as e

import aerospike


@pytest.mark.usefixtures("connection_config")
class TestCreateRole(object):

    config = TestBaseClass.get_connection_config()

    pytestmark = pytest.mark.skipif(
        not TestBaseClass.auth_in_use(), reason="No user specified, may be not secured cluster."
    )

    def setup_method(self, method):
        """
        Setup method
        """
        config = self.config
        self.client = aerospike.client(config).connect(config["user"], config["password"])
        try:
            self.client.admin_drop_user("testcreaterole")
            time.sleep(2)
        except Exception:
            pass  # do nothing, EAFP

        self.delete_users = []

    def teardown_method(self, method):
        """
        Teardown method
        """

        for user in self.delete_users:
            try:
                self.client.admin_drop_user(user)
            except Exception:
                pass

        self.client.close()

    def test_create_role_without_any_parameters(self):

        with pytest.raises(TypeError) as typeError:
            self.client.admin_create_role()

        assert "argument 'role' (pos 1)" in str(typeError.value)

    def test_create_role_positive_with_policy(self):
        """
        Create role positive
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        self.client.admin_create_role(
            "usr-sys-admin-test", [{"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"}], {"timeout": 180000}
        )
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"code": 10, "ns": "test", "set": "demo"}],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 0,
        }

        try:
            status = self.client.admin_create_user("testcreaterole", "createrole", ["usr-sys-admin-test"])
        except e.QuotasNotEnabled:
            pytest.mark.skip(reason="Got QuotasNotEnabled, skipping quota test.")
            pytest.skip()

        assert status == 0
        time.sleep(1)
        roles = self.client.admin_query_user("testcreaterole")

        assert roles == ["usr-sys-admin-test"]

        self.client.admin_drop_user("testcreaterole")

    @pytest.mark.parametrize(
        "priv_name, privs",
        [
            ("PRIV_USER_ADMIN", [{"code": aerospike.PRIV_USER_ADMIN, "ns": "", "set": ""}]),
            ("PRIV_SYS_ADMIN", [{"code": aerospike.PRIV_SYS_ADMIN, "ns": "", "set": ""}]),
            ("PRIV_DATA_ADMIN", [{"code": aerospike.PRIV_DATA_ADMIN, "ns": "", "set": ""}]),
            ("PRIV_READ", [{"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"}]),
            ("PRIV_WRITE", [{"code": aerospike.PRIV_WRITE, "ns": "test", "set": "demo"}]),
            ("PRIV_READ_WRITE", [{"code": aerospike.PRIV_READ_WRITE, "ns": "test", "set": "demo"}]),
            ("PRIV_READ_WRITE_UDF", [{"code": aerospike.PRIV_READ_WRITE_UDF, "ns": "test", "set": "demo"}]),
            ("PRIV_TRUNCATE", [{"code": aerospike.PRIV_TRUNCATE, "ns": "test", "set": "demo"}]),
            ("PRIV_UDF_ADMIN", [{"code": aerospike.PRIV_UDF_ADMIN, "ns": "", "set": ""}]),
            ("PRIV_SINDEX_ADMIN", [{"code": aerospike.PRIV_SINDEX_ADMIN, "ns": "", "set": ""}]),
        ],
    )
    def test_create_role_all_privs_positive(self, priv_name, privs):
        """
        Create role positive
        """

        role_name = "usr-sys-admin-test-" + priv_name

        try:
            self.client.admin_get_role(role_name)
            # role exists, clear it out.
            self.client.admin_drop_role(role_name)
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        self.client.admin_create_role(role_name, privs)
        time.sleep(1)
        roles = self.client.admin_get_role(role_name)
        assert roles == {"privileges": privs, "whitelist": [], "read_quota": 0, "write_quota": 0}

        try:
            status = self.client.admin_create_user("testcreaterole", "createrole", [role_name])
        except e.QuotasNotEnabled:
            pytest.mark.skip(reason="Got QuotasNotEnabled, skipping quota test.")
            pytest.skip()

        assert status == 0
        time.sleep(1)
        roles = self.client.admin_query_user("testcreaterole")

        assert roles == [role_name]

        self.client.admin_drop_user("testcreaterole")

        self.client.admin_drop_role(role_name)

    def test_create_role_positive_with_policy_write(self):
        """
        Create role with write privilege positive
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        self.client.admin_create_role(
            "usr-sys-admin-test", [{"code": aerospike.PRIV_WRITE, "ns": "test", "set": "demo"}]
        )
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"code": 13, "ns": "test", "set": "demo"}],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 0,
        }

        try:
            status = self.client.admin_create_user("testcreaterole", "createrole", ["usr-sys-admin-test"])
        except e.QuotasNotEnabled:
            pytest.mark.skip(reason="Got QuotasNotEnabled, skipping quota test.")
            pytest.skip()

        assert status == 0
        time.sleep(1)
        roles = self.client.admin_query_user("testcreaterole")

        assert roles == ["usr-sys-admin-test"]

        self.client.admin_drop_user("testcreaterole")

    def test_create_role_positive(self):
        """
        Create role positive
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            # Give some time for the role removal to take place
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        self.client.admin_create_role(
            "usr-sys-admin-test", [{"code": aerospike.PRIV_USER_ADMIN}, {"code": aerospike.PRIV_SYS_ADMIN}]
        )
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")

        assert roles == {
            "privileges": [{"code": 0, "ns": "", "set": ""}, {"code": 1, "ns": "", "set": ""}],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 0,
        }

        self.client.admin_drop_role("usr-sys-admin-test")

    def test_create_role_whitelist_quota_positive(self):
        """
        Create role positive
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            # Give some time for the role removal to take place
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        try:
            self.client.admin_create_role(
                "usr-sys-admin-test",
                [{"code": aerospike.PRIV_USER_ADMIN}, {"code": aerospike.PRIV_SYS_ADMIN}],
                whitelist=["127.0.0.1", "10.1.2.0/24"],
                read_quota=20,
                write_quota=30,
            )
        except e.QuotasNotEnabled:
            pytest.mark.skip(reason="Got QuotasNotEnabled, skipping quota test.")
            pytest.skip()

        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")

        assert roles == {
            "privileges": [
                {"code": aerospike.PRIV_USER_ADMIN, "ns": "", "set": ""},
                {"code": aerospike.PRIV_SYS_ADMIN, "ns": "", "set": ""},
            ],
            "whitelist": ["127.0.0.1", "10.1.2.0/24"],
            "read_quota": 20,
            "write_quota": 30,
        }

        self.client.admin_drop_role("usr-sys-admin-test")

    def test_create_role_incorrect_role_type(self):
        """
        role name not string
        """
        with pytest.raises(e.ParamError) as excinfo:
            self.client.admin_create_role(1, [{"code": aerospike.PRIV_USER_ADMIN}])
        assert excinfo.value.code == -2
        assert "Role name should be a string" in excinfo.value.msg

    def test_create_role_unknown_privilege_type(self):
        """
        privilege type unknown
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        with pytest.raises(e.InvalidPrivilege) as excinfo:
            self.client.admin_create_role("usr-sys-admin-test", [{"code": 64}])
        assert excinfo.value.code == 72

    def test_create_role_incorrect_privilege_type(self):
        """
        privilege type incorrect
        """
        with pytest.raises(e.ParamError) as excinfo:
            self.client.admin_create_role("usr-sys-admin-test", None)
        assert excinfo.value.code == -2
        assert excinfo.value.msg == "Privileges should be a list"

    def test_create_role_existing_role(self):
        """
        create an already existing role
        """
        try:
            self.client.admin_get_role("usr-sys-admin-test")
            # role exists, clear it out.
            self.client.admin_drop_role("usr-sys-admin-test")
            time.sleep(2)
        except e.InvalidRole:
            pass  # we are good, no such role exists

        self.client.admin_create_role(
            "usr-sys-admin-test", [{"code": aerospike.PRIV_USER_ADMIN}, {"code": aerospike.PRIV_SYS_ADMIN}]
        )
        time.sleep(1)
        with pytest.raises(e.RoleExistsError) as excinfo:
            self.client.admin_create_role(
                "usr-sys-admin-test", [{"code": aerospike.PRIV_USER_ADMIN}, {"code": aerospike.PRIV_SYS_ADMIN}]
            )
        assert excinfo.value.code == 71
        assert excinfo.value.msg == "AEROSPIKE_ROLE_ALREADY_EXISTS"

        status = self.client.admin_drop_role("usr-sys-admin-test")

        assert status == 0

    def test_create_role_positive_with_special_characters(self):
        """
        Create role positive with special characters in role name
        """
        role_name = "!#Q#AEQ@#$%&^*((^&*~~~````"
        try:
            self.client.admin_drop_role(role_name)  # clear out if it exists
            time.sleep(2)
        except Exception:
            pass  # EAFP
        status = self.client.admin_create_role(
            role_name, [{"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"}]
        )

        assert status == 0
        time.sleep(1)
        roles = self.client.admin_get_role(role_name)

        assert roles == {
            "privileges": [
                {"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"},
            ],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 0,
        }

        status = self.client.admin_create_user("testcreaterole", "createrole", [role_name])

        assert status == 0
        time.sleep(1)
        roles = self.client.admin_query_user("testcreaterole")

        assert roles == [role_name]

        self.client.admin_drop_role(role_name)

        time.sleep(1)

        roles = self.client.admin_query_user("testcreaterole")

        assert roles == []

        self.client.admin_drop_user("testcreaterole")

    def test_create_role_positive_with_too_long_role_name(self):
        """
        Create role positive with too long role name
        """
        role_name = "role$" * 1000

        with pytest.raises(e.InvalidRole) as excinfo:
            self.client.admin_create_role(
                role_name, [{"code": aerospike.PRIV_READ, "ns": "test", "set": "demo"}]
            )
        assert excinfo.value.code == 70
        assert excinfo.value.msg == "AEROSPIKE_INVALID_ROLE"
