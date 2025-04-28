# pygpgme - a Python wrapper for the gpgme library
# Copyright (C) 2006  James Henstridge
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest

def test_suite():
    import gpgme.tests.test_context
    import gpgme.tests.test_keys
    import gpgme.tests.test_keylist
    import gpgme.tests.test_import
    import gpgme.tests.test_export
    import gpgme.tests.test_delete
    import gpgme.tests.test_sign_verify
    import gpgme.tests.test_encrypt_decrypt
    import gpgme.tests.test_passphrase
    import gpgme.tests.test_progress
    import gpgme.tests.test_editkey
    import gpgme.tests.test_genkey

    suite = unittest.TestSuite()

    suite.addTest(gpgme.tests.test_context.test_suite())
    suite.addTest(gpgme.tests.test_keys.test_suite())
    suite.addTest(gpgme.tests.test_keylist.test_suite())
    suite.addTest(gpgme.tests.test_import.test_suite())
    suite.addTest(gpgme.tests.test_export.test_suite())
    suite.addTest(gpgme.tests.test_delete.test_suite())
    suite.addTest(gpgme.tests.test_sign_verify.test_suite())
    suite.addTest(gpgme.tests.test_encrypt_decrypt.test_suite())
    suite.addTest(gpgme.tests.test_passphrase.test_suite())
    suite.addTest(gpgme.tests.test_progress.test_suite())
    suite.addTest(gpgme.tests.test_editkey.test_suite())
    suite.addTest(gpgme.tests.test_genkey.test_suite())

    return suite
