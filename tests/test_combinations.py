import unittest
from glovo.restructure_functions import find_combination
from glovo.restructure_functions import SingleProduct


class TestOptimizeBasket(unittest.TestCase):
    def test_combinations_addon_random(self):  # Edit it aint just product
        # (product_object, basket_min_value, basket_surcharge, delivery_fee)
        basket_min_value = 40
        basket_surcharge = 6
        delivery_fee = 0
        product_to_pass = SingleProduct(
            "prod_name",
            312121,
            20,
            {
                4249843938: {'Blat Philadelphia': 11.0},
                4249843943: {'Blat italian': 0.0},
                4249843954: {'Blat pufos': 0.0},
                4249843963: {'Sos iute - 50g': 6.75}
            }
        )
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.name, "prod_name")
        self.assertEqual(result.id, 312121)
        self.assertEqual(result.addon_name, "Blat italian")
        self.assertEqual(result.addon_id, 4249843943)
        self.assertEqual(result.final_price, 26.99)

    def test_combinations_product_and_addon(self):
        basket_min_value = 24
        basket_surcharge = 10
        delivery_fee = 0
        product_to_pass = SingleProduct(
            "prod_name",
            312121,
            20,
            {
                4249843938: {'Blat Philadelphia': 4.0},
                4249843943: {'Blat italian': 0.0},
                4249843954: {'Blat pufos': 0.0},
                4249843963: {'Sos iute - 50g': 6.75}
            }
        )
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.addon_name, "Blat Philadelphia")
        self.assertEqual(result.addon_id, 4249843938)
        self.assertEqual(result.final_price, 24.99)

    def test_combinations_addon_equal_to_surcharge(self):
        basket_min_value = 24
        basket_surcharge = 4
        delivery_fee = 0
        product_to_pass = SingleProduct(
            "prod_name",
            312121,
            20,
            {
                4249843938: {'Blat Philadelphia': 4.0},
                4249843943: {'Blat italian': 0.0},
                4249843954: {'Blat pufos': 0.0},
                4249843963: {'Sos iute - 50g': 6.75}
            }
        )
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.addon_name, "Blat Philadelphia")
        self.assertEqual(result.addon_id, 4249843938)
        self.assertEqual(result.final_price, 24.99)

    def test_combinations_free_addon(self):
        basket_min_value = 20
        basket_surcharge = 4
        delivery_fee = 0
        product_to_pass = SingleProduct(
            "prod_name",
            312121,
            20,
            {
                4249843938: {'Blat Philadelphia': 0.0}
            }
        )
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.final_price, 20.99)

    def test_combinations_delivery_fee(self):
        basket_min_value = 30
        basket_surcharge = 3
        delivery_fee = 4
        product_to_pass = SingleProduct("prod_name", 312121, 20, {4249843938: {'Blat Philadelphia': 4.0}})
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.price, 27.99)

    def test_combinations_just_product(self):  # edit it aint just product
        basket_min_value = 30
        basket_surcharge = 6
        delivery_fee = 0
        product_to_pass = SingleProduct(
            "prod_name",
            312121,
            20,
            {
                4249843938: {'Blat Philadelphia': 11.0},
                4249843943: {'Blat italian': 9.0},
                4249843954: {'Blat pufos': 8.0},
                4249843963: {'Sos iute - 50g': 7.75}
            }
        )
        result = find_combination(product_to_pass, basket_min_value, basket_surcharge, delivery_fee)
        self.assertEqual(result.name, "prod_name")
        self.assertEqual(result.id, 312121)
        self.assertEqual(result.price, 26.99)


if __name__ == '__main__':
    unittest.main()
