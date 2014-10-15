# (c) 2014, Maciej Delmanowski <drybjed@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from ansible import errors

try:
    import netaddr
except Exception, e:
    raise errors.AnsibleFilterError('python-netaddr package is not installed')


# ---- IP address and network filters ----

def ipaddr(value, query = '', version = False, alias = 'ipaddr'):
    ''' Check if string is an IP address or network and filter it '''

    query_types = [ 'type', 'bool', 'int', 'version', 'size', 'address', 'ip', 'host', \
                    'network', 'subnet', 'prefix', 'broadcast', 'netmask', 'hostmask', \
                    'unicast', 'multicast', 'private', 'public', 'loopback', 'lo', \
                    'revdns', 'wrap', 'ipv6', 'v6', 'ipv4', 'v4' ]

    try:
        v = netaddr.IPAddress(value)
        vtype = 'address'
    except:
        try:
            v = netaddr.IPNetwork(value)
            vtype = 'network'
        except:
            if query and query not in [ 'bool' ]:
                raise errors.AnsibleFilterError(alias + ': not an IP address or network: %s' % value)
            else:
                return False

    if query and query not in query_types and ipaddr(query, 'network'):
        iplist = netaddr.IPNetwork(query)

    if not query and version and v.version != version:
        return False
    elif (query and version and v.version != version) and (query in query_types or iplist):
        return False

    if not query:
        if v:
            return value
        else:
            return False

    elif query == 'type':
        return vtype

    elif query == 'bool':
        if v:
            return True
        else:
            return False

    elif query == 'int':
        if vtype == 'address':
            return int(v)
        else:
            return False

    elif query == 'version':
        return v.version

    elif query == 'size':
        if vtype == 'address':
            return 1
        elif vtype == 'network':
            return v.size

    elif query in [ 'address', 'ip', 'host' ]:
        if vtype == 'address':
            return str(v)
        elif vtype == 'network':
            if v.ip != v.network:
                return str(v.ip)
            else:
                return False
        else:
            return False

    elif query == 'network':
        if vtype == 'network':
            return str(v.network)
        else:
            return False

    elif query == 'subnet':
        if vtype == 'network':
            return str(v.cidr)
        else:
            return False

    elif query == 'prefix':
        if vtype == 'network':
            return str(v.prefixlen)
        else:
            return False

    elif query == 'broadcast':
        if vtype == 'network':
            return str(v.broadcast)
        else:
            return False

    elif query == 'netmask':
        if vtype == 'address' and v.is_netmask():
            return value
        elif vtype == 'network':
            return str(v.netmask)
        else:
            return False

    elif query == 'hostmask':
        if vtype == 'address' and v.is_hostmask():
            return value
        elif vtype == 'network':
            return str(v.hostmask)
        else:
            return False

    elif query == 'unicast':
        if v.is_unicast():
            return value
        else:
            return False

    elif query == 'multicast':
        if v.is_multicast():
            return value
        else:
            return False

    elif query == 'private':
        if v.is_private():
            return value
        else:
            return False

    elif query == 'public':
        if v.is_unicast() and not v.is_private():
            return value
        else:
            return False

    elif query in [ 'loopback', 'lo' ]:
        if vtype == 'address' and v.is_loopback():
            return value
        else:
            return False

    elif query == 'revdns':
        if vtype == 'address':
            return v.reverse_dns
        else:
            return False

    elif query == 'wrap':
        if v.version == 6:
            if vtype == 'address':
                return '[' + str(v) + ']'
            elif vtype == 'network':
                return '[' + str(v.ip) + ']/' + str(v.prefixlen)
        else:
            return value

    elif query in [ 'ipv6', 'v6' ]:
        if v.version == 4:
            return str(v.ipv6())
        else:
            return value

    elif query in [ 'ipv4', 'v4' ]:
        if v.version == 6:
            try:
                return str(v.ipv4())
            except:
                return False
        else:
            return value

    else:
        if iplist:
            try:
                if vtype == 'address' and v in list(iplist):
                    return value
                else:
                    return False
            except Exception, e:
                raise errors.AnsibleFilterError(alias + ': error: %s' % e)

        else:
            raise errors.AnsibleFilterError(alias + ': unknown filter type: %s' % query)


def ipv4(value, query = ''):
    return ipaddr(value, query, version = 4, alias = 'ipv4')


def ipv6(value, query = ''):
    return ipaddr(value, query, version = 6, alias = 'ipv6')


# ---- HWaddr / MAC address filters ----

def hwaddr(value, query = '', alias = 'hwaddr'):
    ''' Check if string is a HW/MAC address and filter it '''

    try:
        v = netaddr.EUI(value)
    except:
        if query and query not in [ 'bool' ]:
            raise errors.AnsibleFilterError(alias + ': not a hardware address: %s' % value)
        else:
            return False

    if not query:
        if v:
            return value
        else:
            return False

    elif query == 'bool':
        if v:
            return True
        else:
            return False

    elif query in [ 'win', 'eui48' ]:
        v.dialect = netaddr.mac_eui48
        return str(v)

    elif query == 'unix':
        v.dialect = netaddr.mac_unix
        return str(v)

    elif query in [ 'pgsql', 'postgresql', 'psql' ]:
        v.dialect = netaddr.mac_pgsql
        return str(v)

    elif query == 'cisco':
        v.dialect = netaddr.mac_cisco
        return str(v)

    elif query == 'bare':
        v.dialect = netaddr.mac_bare
        return str(v)

    elif query == 'linux':
        v.dialect = mac_linux
        return str(v)

    else:
        raise errors.AnsibleFilterError(alias + ': unknown filter type: %s' % query)

class mac_linux(netaddr.mac_unix): pass
mac_linux.word_fmt = '%.2x'


def macaddr(value, query = ''):
    return hwaddr(value, query, alias = 'macaddr')


# ---- Ansible filters ----

class FilterModule(object):
    ''' IP address and network manipulation filters '''

    def filters(self):
        return {

            # IP addresses and networks
            'ipaddr': ipaddr,
            'ipv4': ipv4,
            'ipv6': ipv6,

            # MAC / HW addresses
            'hwaddr': hwaddr,
            'macaddr': macaddr

        }
