import irc_wheat
import sys


def parse_date(d):
    """Parse date string to (yyyy, MM, dd)

        :param d: the date string to parse
        :returns: parsed date as tuple or None on error
    """
    date_fields = d.split('-')
    if date_fields and len(date_fields) == 3:
        return (int(date_fields[0]), int(date_fields[1]), int(date_fields[2]))
    else:
        return None


def harvest_channel(channel, start_date, end_date, exclude_nicks=None,
                    exclude_posts=None):
    """Pull all matching irc posts

       :param channel: the irc channel to search
       :param start_date: the starting date of irc entries
       :param end_date: the ending date of irc entries
       :param exclude_nicks: the irc nicknames whose posts are to be ignored
       :param exclude_posts: the substrings to cause posts to be ignored
    """

    start_fields = parse_date(start_date)
    end_fields = parse_date(end_date)

    if not start_fields or not end_fields:
        return

    start_year = start_fields[0]
    start_month = start_fields[1]
    start_day = start_fields[2]

    end_year = end_fields[0]
    end_month = end_fields[1]
    end_day = end_fields[2]

    days_in_month = {}
    days_in_month['1'] = 31
    days_in_month['2'] = 28
    days_in_month['3'] = 31
    days_in_month['4'] = 30
    days_in_month['5'] = 31
    days_in_month['6'] = 30
    days_in_month['7'] = 31
    days_in_month['8'] = 31
    days_in_month['9'] = 30
    days_in_month['10'] = 31
    days_in_month['11'] = 30
    days_in_month['12'] = 31

    pulling_data = True
    current_year = start_year
    current_month = start_month
    current_day = start_day

    while pulling_data:
        current_date = '%d-%02d-%02d' % (current_year,
                                         current_month,
                                         current_day)
        log_entries = irc_wheat.get_channel_entries(channel,
                                                    current_date,
                                                    exclude_nicks,
                                                    exclude_posts)
        if log_entries:
            irc_wheat.print_irc_entries(log_entries)

        if current_year == end_year and \
           current_month == end_month and \
           current_day == end_day:
            pulling_data = False
        else:
            if current_day < days_in_month[str(current_month)]:
                current_day += 1
            else:
                current_month += 1
                current_day = 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('usage: python %s channel start_date end_date' % sys.argv[0])
        sys.exit(1)
    exclude_nicks = ['openstackgerrit']
    exclude_posts = [' has joined ',
                     ' has quit IRC']

    harvest_channel(sys.argv[1],
                    sys.argv[2],
                    sys.argv[3],
                    exclude_nicks,
                    exclude_posts)
