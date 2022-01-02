from .launchpad_mini_mk3_augmented import Launchpad_Mini_MK3_Augmented
import Launchpad_Mini_MK3


def get_capabilities():
    Launchpad_Mini_MK3.get_capabilities()


def create_instance(c_instance):
    return Launchpad_Mini_MK3_Augmented(c_instance=c_instance)
