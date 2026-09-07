import random
import unittest

from core import RoundRobinPolicy, Server
from exporter import summarize
from simulation import SimulationResult
from traffic import BurstTrafficGenerator


class TrafficTests(unittest.TestCase):
    def test_burst_generator_preserves_burst_state(self):
        generator = BurstTrafficGenerator(3, 30.0, 0.8, random.Random(7))
        generator.next_interarrival()
        self.assertEqual(generator.remaining, 2)
        generator.next_interarrival()
        generator.next_interarrival()
        self.assertEqual(generator.remaining, 0)


class PolicyTests(unittest.TestCase):
    def test_round_robin_cycles_servers(self):
        policy = RoundRobinPolicy()
        servers = [object(), object(), object()]
        selected = [servers.index(policy.select(servers, random.Random(1))) for _ in range(6)]
        self.assertEqual(selected, [0, 1, 2, 0, 1, 2])


class StatisticsTests(unittest.TestCase):
    def test_summary_contains_confidence_intervals_and_little_law(self):
        results = [
            SimulationResult("random", 0.6, seed, 0.6, 1.0, 0.6, [0.2, 0.2, 0.2], 10, 10, 0, 10)
            for seed in (1, 2, 3)
        ]
        row = summarize(results, 1.0, 3)[0]
        self.assertIn("throughput_ci95", row)
        self.assertIn("response_time_ci95", row)
        self.assertIn("u1_ci95", row)
        self.assertTrue(row["little_law_ok"])


if __name__ == "__main__":
    unittest.main()
