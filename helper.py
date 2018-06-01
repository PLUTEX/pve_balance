import logging
from string import Formatter


default_suffixes = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB')
default_factor = 1024


class ByteFormatter(Formatter):
    def __init__(self, factor=default_factor, suffixes=default_suffixes):
        self.factor = factor
        self.suffixes = suffixes
        self.suffix = None

    def format_field(self, value, format_spec):
        if self.suffix == 'B':
            format_spec = '.0f'
        elif self.suffix:
            format_spec = '.3g'

        result = super().format_field(value, format_spec)

        if self.suffix:
            result += ' ' + self.suffix
            self.suffix = None

        return result

    def convert_field(self, value, conversion):
        if conversion == 'b':
            for suffix in self.suffixes:
                if abs(value) < self.factor:
                    self.suffix = suffix
                    return value
                value /= self.factor
        else:
            return super().convert_field(value, conversion)


class Message:
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args
        self.formatter = ByteFormatter()

    def __str__(self):
        return self.formatter.format(self.fmt, *self.args)


class ByteLoggerAdapter(logging.LoggerAdapter):
    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)


def get_logger(name):
    return ByteLoggerAdapter(logging.getLogger(name), {})
