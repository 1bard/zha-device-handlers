from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zigpy.zcl.clusters.general import (
    Alarms,
    Basic,
    GreenPowerProxy,
    Groups,
    Identify,
    Ota,
    PowerConfiguration,
    Scenes,
    Time,
)
from zigpy.zcl.clusters.homeautomation import ElectricalMeasurement
from zigpy.zcl.clusters.hvac import Thermostat, UserInterface
from zigpy.zcl.clusters.smartenergy import Metering

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)


class FilteredMeteringCluster(CustomCluster, Metering):
    """Metering cluster implementation.
    Filters out random incorrect data.
    Device will sometimes use boot-time value of current_summ_delivered,
    then switch back to correct value next update.
    """

    cluster_id = Metering.cluster_id

    _prev_summation_value = 0

    def _update_attribute(self, attrid, value):
        if attrid == 0x0000:
            if self._prev_summation_value == 0:
                self._prev_summation_value = value
            if self._prev_summation_value <= value <= self._prev_summation_value + 1000:
                return
            self._prev_summation_value = value
        super()._update_attribute(attrid, value)


class NamronHeater(CustomDevice):
    """namron.heater"""

    signature = {
        MODELS_INFO: [
            ("NAMRON AS", "5401392"),
            ("NAMRON AS", "5401393"),
            ("NAMRON AS", "5401394"),
            ("NAMRON AS", "5401395"),
            ("NAMRON AS", "5401396"),
            ("NAMRON AS", "5401397"),
            ("NAMRON AS", "5401398"),
        ],
        ENDPOINTS: {
            # SimpleDescriptor(endpoint=11, profile=260, device_type=10,
            # device_version=1,
            # input_clusters=[0, 1, 3, 5, 4, 257, 65186],
            # output_clusters=[25])
            1: {
                PROFILE_ID: 260,
                DEVICE_TYPE: zha.DeviceType.THERMOSTAT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    Alarms.cluster_id,
                    Time.cluster_id,
                    Thermostat.cluster_id,
                    UserInterface.cluster_id,
                    Metering.cluster_id,
                    ElectricalMeasurement.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    PowerConfiguration.cluster_id,
                    Identify.cluster_id,
                    Ota.cluster_id,
                ],
            },
            242: {
                PROFILE_ID: 41440,
                DEVICE_TYPE: 0x0061,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }
    replacement = {
        ENDPOINTS: {
            1: {
                INPUT_CLUSTERS: [
                    Basic,
                    Identify,
                    Groups,
                    Scenes,
                    Alarms,
                    Time,
                    Thermostat,
                    UserInterface,
                    FilteredMeteringCluster,
                    ElectricalMeasurement,
                ],
                OUTPUT_CLUSTERS: [
                    PowerConfiguration,
                    Identify,
                    Ota,
                ],
            },
            242: {
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy],
            },
        },
    }
