from ipaddress import ip_address


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        client_ip = forwarded_for.split(',', 1)[0].strip()
    else:
        client_ip = ''

    if not client_ip:
        client_ip = request.META.get('REMOTE_ADDR') or 'unknown'

    if client_ip.startswith('['):
        closing_bracket = client_ip.find(']')
        if closing_bracket != -1:
            address = client_ip[1:closing_bracket]
            suffix = client_ip[closing_bracket + 1:]
            if not suffix or (suffix.startswith(':') and suffix[1:].isdecimal()):
                try:
                    if ip_address(address).version == 6:
                        return address
                except ValueError:
                    pass
    else:
        try:
            ip_address(client_ip)
        except ValueError:
            address, separator, port = client_ip.rpartition(':')
            if separator and port.isdecimal():
                try:
                    if ip_address(address).version == 4:
                        return address
                except ValueError:
                    pass

    return client_ip
