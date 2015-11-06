import requests
import sys
import urllib


def get_openstack_irc_daily_page(channel, date):
    """Retrieve postings for irc channel on specified date

       :param: channel the openstack channel of interest
       :param: date the date of postings to retrieve
       :returns: HTML page on success or None on error
    """

    url = 'http://eavesdrop.openstack.org/irclogs/%s/%s.%s.log.html' % \
        (urllib.quote(channel), urllib.quote(channel), date)
    response = requests.get(url)
    if 200 == response.status_code:
        return response.content
    else:
        return None


def html_decode(s):
    """Decode HTML page

       :param: s the HTML fragment to decode
       :returns: the decoded HTML fragment
    """

    if s.find('&quot;') > -1:
        s = s.replace('&quot;', '"')
    if s.find('&gt;') > -1:
        s = s.replace('&gt;', '>')
    if s.find('&lt;') > -1:
        s = s.replace('&lt;', '<')
    if s.find('&amp;') > -1:
        s = s.replace('&amp;', '&')
    if s.find('&nbsp;') > -1:
        s = s.replace('&nbsp;', ' ')

    return s


def parse_page(page_source, exclude_nicks=None, exclude_posts=None):
    """This is a hacked-up pile of rubbish -- thrown together

       :param: page_source the HTML response page of IRC postings
       :param: exclude_nicks irc nicknames to exclude
       :param: exclude_posts irc post substrings to exclude
       :returns: list of parsed IRC postings or None on error
    """

    log_entries = []
    start_table_marker = '<table class="irclog">'
    end_table_marker = '</table>'
    pos_start_table = page_source.find(start_table_marker)
    if pos_start_table > 0:
        pos_end_table = page_source.find(end_table_marker, pos_start_table)
        if pos_end_table > 0:
            pos_start_entries = pos_start_table + len(start_table_marker)
            markup_entries = page_source[pos_start_entries:pos_end_table]
            pos = 0
            parsing = True
            while parsing:
                timestamp = None
                nick = None
                irc_post = None
                pos_row_start = markup_entries.find('<tr ', pos)
                pos_end_tr_start_decl = markup_entries.find('>', pos_row_start)
                pos_row_end = markup_entries.find('</tr>', pos_row_start)
                if pos_row_start > -1 and \
                   pos_end_tr_start_decl > -1 and \
                   pos_row_end > -1:
                    pos_id_start = markup_entries.find(' id="', pos)
                    if pos_id_start > 0:
                        pos_id_end = markup_entries.find('"', pos_id_start+5)
                        if pos_id_end > -1:
                            pos_ts_start = pos_id_start + 5
                            timestamp = markup_entries[pos_ts_start:pos_id_end]
                            timestamp = timestamp[1:]
                    pos_start_tr_text = pos_end_tr_start_decl + 1
                    tr_text = markup_entries[pos_start_tr_text:pos_row_end]
                    exclude_post = False
                    if exclude_posts:
                        for exclusion in exclude_posts:
                            if tr_text.find(exclusion) != -1:
                                exclude_post = True
                                break
                    if not exclude_post:
                        tr_text = tr_text.strip()
                        if tr_text:
                            pos_start_th = tr_text.find('<th ')
                            pos_end_th = tr_text.find('</th>')
                            if pos_start_th > -1 and pos_end_th > -1:
                                pos_gt = tr_text.find('>', pos_start_th)
                                if pos_gt > -1:
                                    nick = tr_text[pos_gt+1:pos_end_th].strip()
                                    if nick:
                                        pos_start_td = tr_text.find('<td ',
                                                                    pos_end_th)
                                        pos_end_td = tr_text.find('</td>',
                                                                  pos_end_th)
                                        pos_gt = tr_text.find('>',
                                                              pos_end_th+5)
                                        if pos_start_td > -1 and \
                                           pos_end_td > -1 and \
                                           pos_gt > -1:
                                            b = pos_gt + 1
                                            e = pos_end_td
                                            irc_post = tr_text[b:e].strip()
                    if timestamp and nick and irc_post:
                        exclude_nick = exclude_nicks and nick in exclude_nicks
                        if not exclude_nick:
                            irc_post = html_decode(irc_post)
                            log_entries.append((timestamp, nick, irc_post))
                    pos = pos_row_end + 5
                else:
                    parsing = False

    return log_entries


def get_channel_entries(channel, date, exclude_nicks=None, exclude_posts=None):
    """Retrieve list of irc channel postings

       :param: channel the irc channel
       :param: the date of retrieved postings
       :return: list of postings or None
    """

    page = get_openstack_irc_daily_page(channel, date)
    if page is not None:
        log_entries = parse_page(page, exclude_nicks, exclude_posts)
        if log_entries:
            return log_entries
        else:
            print('warning: no entries found')
            return None
    else:
        print('warning: page not found %s %s' % (channel, date))
        return None


def print_irc_entries(log_entries):
    """Print out irc entries to stdout

       :param: log_entries list of entries to print
    """
    for log_entry in log_entries:
        print('%s %s %s' % (log_entry[0], log_entry[1], log_entry[2]))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python %s irc_channel date' % sys.argv[0])
        sys.exit(1)
    channel = sys.argv[1]
    date = sys.argv[2]
    irc_log_entries = get_channel_entries(channel, date)
    if irc_log_entries:
        print_irc_entries(irc_log_entries)
