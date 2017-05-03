import unittest
import api


class ApiServerTestCase(unittest.TestCase):
    def test_create_employee_query(self):
        employee = {
            "phone": "1-412-741-5187x835",
            "age": 25,
            "departmentId": "LB-4",
            "jobTitle": "Executive",
            "name": "Eric Garcia",
            "departmentName": "Finance",
            "departmentActivityLevel": "low",
            "id": "LBE-104",
            "salary": 2093
        }
        
        
        self.assertTrue(api.create_employee_query(age_range=(25, 50)).test(employee))
        self.assertFalse(api.create_employee_query(age_range=(26, 50)).test(employee))
        self.assertFalse(api.create_employee_query(age_range=(20, 25)).test(employee))
        self.assertTrue(api.create_employee_query(age_range=(20, 26)).test(employee))

        self.assertTrue(api.create_employee_query(keyword="cutive").test(employee))
        self.assertTrue(api.create_employee_query(keyword="Garcia").test(employee))
        self.assertFalse(api.create_employee_query(keyword="foo").test(employee))

        self.assertTrue(api.create_employee_query(department_name="Finance").test(employee))
        self.assertFalse(api.create_employee_query(department_name="Operation").test(employee))

        self.assertTrue(api.create_employee_query(
            age_range=(25, 50), keyword="Garcia", department_name="Finance"
        ).test(employee))
        
        self.assertRaises(ValueError, api.create_employee_query)
        
    def test_send_employees_for_training(self):
        '''
        The below commeneted text case will cover for few functionality.Since the called function involves databse entry, we need to use mock up test cases.
        '''
        #self.assertRaises(ValueError, api.send_employees_for_training)
        #self.assertRaises(ValueError, api.send_employees_for_training,ID="LBE-130")
        pass
        
        


if __name__ == '__main__':
    unittest.main()
