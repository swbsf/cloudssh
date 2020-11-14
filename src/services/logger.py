from loguru import logger
import sys


def print_orange(message):
    logger.remove()
    logger.add(sys.stdout, format="<yellow>{message}</yellow>")
    logger.info(message)


def print_green(message):
    logger.remove()
    logger.add(sys.stdout, format="<green>{message}</green>")
    logger.warning(message)


def print_red(message):
    logger.remove()
    logger.add(sys.stdout, format="<red>{message}</red>")
    logger.error(message)


def print_red_and_exit(message):
    logger.remove()
    logger.add(sys.stdout, format="<red>{message}</red>")
    logger.error(message)
    sys.exit(1)


def print_light_grey(message):
    logger.remove()
    logger.add(sys.stdout, format="<dim><white>{message}</white></dim>")
    logger.error(message)
