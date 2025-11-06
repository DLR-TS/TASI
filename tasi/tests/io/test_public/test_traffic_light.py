from datetime import datetime, timedelta
from unittest import TestCase

from tasi.io import TrafficLight, TrafficLightState


class TrafficLightTestCase(TestCase):

    def test_init_traffic_light_state(self):

        tls = TrafficLightState(red=True)

        for attr in ["amber", "green", "unknown"]:
            self.assertFalse(getattr(tls, attr))

        self.assertEqual(tls.other, -1)

    def test_init_traffic_light(self):

        tls = TrafficLight(
            index=0,
            timestamp=datetime.now(),
            flashing=False,
            state=TrafficLightState(red=True),
        )

        self.assertEqual(tls.index, 0)
        self.assertFalse(tls.flashing)


class TrafficLightConversionTestCase(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.tl = TrafficLight(
            index=0,
            timestamp=datetime.now(),
            flashing=False,
            state=TrafficLightState(red=True),
        )

    def test_convert_json(self):
        self.tl.model_dump_json()

    def test_convert_tasi(self):
        tasi = self.tl.as_tasi(as_record=False)

        tl = TrafficLight.from_tasi(tasi)

        self.assertEqual(tl.timestamp, self.tl.timestamp)
        self.assertEqual(tl.flashing, self.tl.flashing)
        self.assertEqual(tl.index, self.tl.index)

        for attr in ["red", "amber", "green", "unknown"]:
            self.assertEqual(getattr(tl.state, attr), getattr(self.tl.state, attr))
