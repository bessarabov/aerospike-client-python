# -*- coding: utf-8 -*-

import pytest
import time
from .test_base_class import TestBaseClass
from aerospike import exception as e

import aerospike


class TestSetQuotas(TestBaseClass):
    def setup_method(self, method):
        """
        Setup method
        """
        self.client = TestBaseClass.get_new_connection()
        if TestBaseClass.auth_in_use() is False:
            pytest.skip("No user specified, may not be a secured cluster", allow_module_level=True)

        usr_sys_admin_privs = [{"code": aerospike.PRIV_USER_ADMIN}, {"code": aerospike.PRIV_SYS_ADMIN}]
        try:
            self.client.admin_drop_role("usr-sys-admin-test")
            time.sleep(2)
        except Exception:
            pass

        try:
            self.client.admin_create_role("usr-sys-admin-test", usr_sys_admin_privs, write_quota=4500)
        except e.QuotasNotEnabled:
            pytest.skip(reason="Got QuotasNotEnabled, skipping quota test.")

        time.sleep(1)

    def teardown_method(self, method):
        """
        Teardown method
        """
        try:
            self.client.admin_drop_role("usr-sys-admin-test")
        except Exception:
            pass

    def test_admin_set_quota_no_parameters(self):
        """
        Set quotas with no parameters.
        """
        with pytest.raises(TypeError):
            self.client.admin_set_quotas()

    def test_admin_set_quota_no_quotas_positive(self):
        """
        Set quotas with no quotas. (will reset quotas on a role with existing quotas)
        """
        self.client.admin_set_quotas(
            role="usr-sys-admin-test",
        )
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"ns": "", "set": "", "code": 0}, {"ns": "", "set": "", "code": 1}],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 4500,
        }

    def test_admin_set_quota_one_quota_positive(self):
        """
        Set quotas with one quota.
        """
        self.client.admin_set_quotas(role="usr-sys-admin-test", read_quota=250)
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"ns": "", "set": "", "code": 0}, {"ns": "", "set": "", "code": 1}],
            "whitelist": [],
            "read_quota": 250,
            "write_quota": 4500,
        }

    def test_admin_set_quota_positive(self):
        """
        Set Quota positive
        """
        self.client.admin_set_quotas(role="usr-sys-admin-test", read_quota=250, write_quota=300)
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"ns": "", "set": "", "code": 0}, {"ns": "", "set": "", "code": 1}],
            "whitelist": [],
            "read_quota": 250,
            "write_quota": 300,
        }

    def test_admin_set_quota_positive_reset(self):
        """
        Set Quota positive
        """
        self.client.admin_set_quotas(role="usr-sys-admin-test", read_quota=0, write_quota=0)
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"ns": "", "set": "", "code": 0}, {"ns": "", "set": "", "code": 1}],
            "whitelist": [],
            "read_quota": 0,
            "write_quota": 0,
        }

    def test_admin_set_quota_positive_with_policy(self):
        """
        Set Quota positive policy
        """
        self.client.admin_set_quotas(
            role="usr-sys-admin-test", read_quota=250, write_quota=300, policy={"timeout": 180000}
        )
        time.sleep(1)
        roles = self.client.admin_get_role("usr-sys-admin-test")
        assert roles == {
            "privileges": [{"ns": "", "set": "", "code": 0}, {"ns": "", "set": "", "code": 1}],
            "whitelist": [],
            "read_quota": 250,
            "write_quota": 300,
        }

    def test_admin_set_quota_incorrect_role_name(self):
        """
        Incorrect role name
        """
        with pytest.raises(e.InvalidRole) as excinfo:
            self.client.admin_set_quotas(
                role="bad-role-name", read_quota=250, write_quota=300
            )
        assert excinfo.value.code == 70
        assert excinfo.value.msg == "AEROSPIKE_INVALID_ROLE"

    def test_admin_set_quota_incorrect_role_type(self):
        """
        Incorrect role type
        """
        with pytest.raises(e.ParamError) as excinfo:
            self.client.admin_set_quotas(role=None, read_quota=250, write_quota=300)
        assert excinfo.value.code == -2
        assert excinfo.value.msg == "Role name should be a string."

    def test_admin_set_quota_incorrect_quota(self):
        """
        Incorrect role name
        """
        try:
            self.client.admin_set_quotas(
                role="usr-sys-admin-test", read_quota=-20, write_quota=300
            )

        except e.InvalidRole as exception:
            assert exception.code == 70
            assert exception.msg == "AEROSPIKE_INVALID_ROLE"

    def test_admin_set_quota_incorrect_quota_type(self):
        """
        Incorrect role type
        """
        with pytest.raises(e.ParamError) as excinfo:
            self.client.admin_set_quotas(
                role="usr-sys-admin-test", read_quota=None, write_quota=300
            )
        assert excinfo.value.code == -2
        assert excinfo.value.msg == "py_read_quota must be an integer."
