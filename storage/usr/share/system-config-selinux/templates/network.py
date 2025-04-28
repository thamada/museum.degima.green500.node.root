te_port_types="""
type TEMPLATETYPE_port_t;
corenet_port(TEMPLATETYPE_port_t)
"""

te_network="""\
sysnet_dns_name_resolve(TEMPLATETYPE_t)
corenet_all_recvfrom_unlabeled(TEMPLATETYPE_t)
"""

te_tcp="""\
allow TEMPLATETYPE_t self:tcp_socket create_stream_socket_perms;
corenet_tcp_sendrecv_all_if(TEMPLATETYPE_t)
corenet_tcp_sendrecv_all_nodes(TEMPLATETYPE_t)
corenet_tcp_sendrecv_all_ports(TEMPLATETYPE_t)
"""

te_in_tcp="""\
corenet_tcp_bind_all_nodes(TEMPLATETYPE_t)
"""

te_in_need_port_tcp="""\
allow TEMPLATETYPE_t TEMPLATETYPE_port_t:tcp_socket name_bind;
"""

te_out_need_port_tcp="""\
allow TEMPLATETYPE_t TEMPLATETYPE_port_t:tcp_socket name_connect;
"""

te_udp="""\
allow TEMPLATETYPE_t self:udp_socket { create_socket_perms listen };
corenet_udp_sendrecv_all_if(TEMPLATETYPE_t)
corenet_udp_sendrecv_all_nodes(TEMPLATETYPE_t)
corenet_udp_sendrecv_all_ports(TEMPLATETYPE_t)
"""

te_in_udp="""\
corenet_udp_bind_all_nodes(TEMPLATETYPE_t)
"""

te_in_need_port_udp="""\
allow TEMPLATETYPE_t TEMPLATETYPE_port_t:udp_socket name_bind;
"""

te_out_all_ports_tcp="""\
corenet_tcp_connect_all_ports(TEMPLATETYPE_t)
"""

te_out_reserved_ports_tcp="""\
corenet_tcp_connect_all_rpc_ports(TEMPLATETYPE_t)
"""

te_out_unreserved_ports_tcp="""\
corenet_tcp_connect_all_unreserved_ports(TEMPLATETYPE_t)
"""

te_in_all_ports_tcp="""\
corenet_tcp_bind_all_ports(TEMPLATETYPE_t)
"""

te_in_reserved_ports_tcp="""\
corenet_tcp_bind_all_rpc_ports(TEMPLATETYPE_t)
"""

te_in_unreserved_ports_tcp="""\
corenet_tcp_bind_all_unreserved_ports(TEMPLATETYPE_t)
"""

te_in_all_ports_udp="""\
corenet_udp_bind_all_ports(TEMPLATETYPE_t)
"""

te_in_reserved_ports_udp="""\
corenet_udp_bind_all_rpc_ports(TEMPLATETYPE_t)
"""

te_in_unreserved_ports_udp="""\
corenet_udp_bind_all_unreserved_ports(TEMPLATETYPE_t)
"""

