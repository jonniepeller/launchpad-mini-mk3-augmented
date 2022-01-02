from novation.novation_base import NovationBase

from .channel_strip_component_augmented import ChannelStripComponentAugmented
from .mixer_component_augmented import MixerComponentAugmented


class NovationBaseAugmented(NovationBase):
    mixer_class = MixerComponentAugmented
    channel_strip_class = ChannelStripComponentAugmented
