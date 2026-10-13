import unittest

from main import Bicycle, Bus, Car, ElectricCar, Transport


class TransportTests(unittest.TestCase):
    def test_transport_is_abstract(self):
        with self.assertRaises(TypeError):
            Transport("Транспорт", 50, 5)

    def test_car_trip(self):
        car = Car("Toyota", 100, 5)
        self.assertEqual(car.move(100), 1.0)
        self.assertAlmostEqual(car.fuel_consumption(100), 7.0)
        self.assertAlmostEqual(car.calculate_cost(100, 60), 420.0)

    def test_bus_trip_and_overload_boundary(self):
        bus = Bus("Богдан", 50, 40, 40)
        self.assertEqual(bus.move(100), 2.0)
        self.assertAlmostEqual(bus.fuel_consumption(100), 15.0)
        self.assertAlmostEqual(bus.calculate_cost(100, 60), 900.0)
        self.assertNotIn("Перевантажено!", bus.info())
        bus.passengers = 41
        self.assertIn("Перевантажено!", bus.info())

    def test_bicycle_speed_and_fuel(self):
        bicycle = Bicycle("Trek", 30)
        self.assertEqual(bicycle.speed, 20)
        self.assertEqual(bicycle.move(100), 5.0)
        self.assertEqual(bicycle.fuel_consumption(100), 0.0)
        self.assertEqual(bicycle.calculate_cost(100, 60), 0.0)
        self.assertEqual(Bicycle("Повільний", 10).move(100), 10.0)

    def test_electric_car_uses_inherited_cost_with_battery(self):
        car = ElectricCar("Leaf", 80, 5)
        self.assertIsInstance(car, Car)
        self.assertIs(ElectricCar.calculate_cost, Transport.calculate_cost)
        self.assertEqual(car.move(100), 1.25)
        self.assertEqual(car.fuel_consumption(100), 0.0)
        self.assertEqual(car.battery_usage(100), 20.0)
        self.assertEqual(car.calculate_cost(100, 5), 100.0)

    def test_zero_distance_for_all_transports(self):
        for transport in [Car("C", 100, 5), Bus("B", 50, 40), Bicycle("V", 20), ElectricCar("E", 80, 5)]:
            with self.subTest(transport=type(transport).__name__):
                self.assertEqual(transport.move(0), 0.0)
                self.assertEqual(transport.fuel_consumption(0), 0.0)
                self.assertEqual(transport.calculate_cost(0, 60), 0.0)

    def test_invalid_inputs(self):
        for invalid_speed in [0, -1, 1.5, True]:
            with self.subTest(speed=invalid_speed), self.assertRaises(ValueError):
                Bicycle("Trek", invalid_speed)
        with self.assertRaises(ValueError):
            Bus("Богдан", 50, 40, -1)
        car = ElectricCar("Leaf", 80, 5)
        for operation in [car.move, car.fuel_consumption, car.battery_usage]:
            with self.assertRaises(ValueError):
                operation(-1)
        with self.assertRaises(ValueError):
            car.calculate_cost(100, -5)


if __name__ == "__main__":
    unittest.main()
