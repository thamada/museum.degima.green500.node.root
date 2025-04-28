RDS(7)									RDS(7)



NAME
       RDS - Reliable Datagram Sockets

SYNOPSIS
       #include <sys/socket.h>
       #include <netinet/in.h>

DESCRIPTION
       This  is an implementation of the RDS socket API. It provides reliable,
       in-order datagram delivery between sockets over	a  variety  of	trans‐
       ports.

       Currently,  RDS	can be transported over Infiniband, and loopback.
       iWARP bcopy is supported, but not RDMA operations.

       RDS uses standard AF_INET addresses as described in ip(7)  to  identify
       end points.

   Socket Creation
       RDS is still in development and as such does not have a reserved proto‐
       col family constant. Applications must read the	string	representation
       of  the	protocol  family  value	 from the pf_rds sysctl parameter file
       described below.

       rds_socket = socket(pf_rds, SOCK_SEQPACKET, 0);


   Socket Options
       RDS sockets support a number of socket  options	through	 the  setsock‐
       opt(2)  and  getsockopt(2)  calls.  The following generic options (with
       socket level SOL_SOCKET) are of specific importance:

       SO_RCVBUF
	      Specifies the size of the receive buffer. See section  on	 "Con‐
	      gestion Control" below.

       SO_SNDBUF
	      Specifies	 the  size  of the send buffer. See "Message Transmis‐
	      sion" below.

       SO_SNDTIMEO
	      Specifies the send timeout when trying to enqueue a message on a
	      socket with a full queue in blocking mode.

       In  addition  to	 these,	 RDS  supports	a  number of protocol specific
       options (with socket level SOL_RDS).  Just as  with  the	 RDS  protocol
       family, an official value has not been assigned yet, so the kernel will
       assign a value dynamically.  The assigned value can be  retrieved  from
       the sol_rds sysctl parameter file.

       RDS  specific  socket  options  will be described in a separate section
       below.

   Binding
       A new RDS socket has no local address when it is	 first	returned  from
       socket(2).   It	must  be  bound	 to a local address by calling bind(2)
       before any messages can be sent or received. This will also attach  the
       socket  to  a  specific	transport,  based on the type of interface the
       local address is attached to.  From that point on, the socket can  only
       reach destinations which are available through this transport.

       For  instance,  when  binding to the address of an Infiniband interface
       such as ib0, the socket will use the Infiniband transport.  If  RDS  is
       not  able  to  associate	 a  transport  with the given address, it will
       return EADDRNOTAVAIL.

       An RDS socket can only be bound to one address and only one socket  can
       be  bound  to a given address/port pair. If no port is specified in the
       binding address then an unbound port is selected at random.

       RDS does not allow the application to bind a previously bound socket to
       another address. Binding to the wildcard address INADDR_ANY is not per‐
       mitted either.

   Connecting
       The default mode of operation for RDS is to use unconnected socket, and
       specify	a destination address as an argument to sendmsg.  However, RDS
       allows sockets to be connected to a remote end point using  connect(2).
       If a socket is connected, calling sendmsg without specifying a destina‐
       tion address will use the previously given remote address.

   Congestion Control
       RDS does not have explicit congestion  control  like  common  streaming
       protocols  such	as TCP. However, sockets have two queue limits associ‐
       ated with them; the send queue size and the receive queue  size.	  Mes‐
       sages are accounted based on the number of bytes of payload.

       The send queue size limits how much data local processes can queue on a
       local socket (see the following section). If that  limit	 is  exceeded,
       the  kernel will not accept further messages until the queue is drained
       and messages have been delivered to  and	 acknowledged  by  the	remote
       host.

       The receive queue size limits how much data RDS will put on the receive
       queue of a socket before marking	 the  socket  as  congested.   When  a
       socket  becomes congested, RDS will send a congestion map update to the
       other participating hosts, who are then expected to stop	 sending  more
       messages to this port.

       There  is a timing window during which a remote host can still continue
       to send messages to a congested port;  RDS  solves  this	 by  accepting
       these  messages	even if the socket's receive queue is already over the
       limit.

       As the application pulls incoming messages off the receive queue	 using
       recvmsg(2),  the	 number	 of bytes on the receive queue will eventually
       drop below the receive queue size, at which  point  the	port  is  then
       marked  uncongested,  and another congestion update is sent to all par‐
       ticipating hosts. This tells them to allow applications to  send	 addi‐
       tional messages to this port.

       The  default values for the send and receive buffer size are controlled
       by the A given  RDS  socket  has	 limited  transmit  buffer  space.  It
       defaults	 to  the  system  wide	socket	send  buffer  size  set in the
       wmem_default and rmem_default sysctls, respectively. They can be	 tuned
       by  the application through the SO_SNDBUF and SO_RCVBUF socket options.


   Blocking Behavior
       The sendmsg(2) and recvmsg(2) calls can block in a  variety  of	situa‐
       tions.	Whether	 a call blocks or returns with an error depends on the
       non-blocking setting of the file descriptor and the  MSG_DONTWAIT  mes‐
       sage flag. If the file descriptor is set to blocking mode (which is the
       default), and the MSG_DONTWAIT flag is not given, the call will	block.

       In addition, the SO_SNDTIMEO and SO_RCVTIMEO socket options can be used
       to specify a timeout (in seconds) after which the call will abort wait‐
       ing,  and return an error. The default timeout is 0, which tells RDS to
       block indefinitely.

   Message Transmission
       Messages may be sent using sendmsg(2) once the  RDS  socket  is	bound.
       Message	length	cannot exceed 4 gigabytes as the wire protocol uses an
       unsigned 32 bit integer to express the message length.

       RDS does not support out of band data. Applications are allowed to send
       to unicast addresses only; broadcast or multicast are not supported.

       A  successful sendmsg(2) call puts the message in the socket's transmit
       queue where it will remain until either	the  destination  acknowledges
       that the message is no longer in the network or the application removes
       the message from the send queue.

       Messages can be removed from the send queue with the RDS_CANCEL_SENT_TO
       socket option described below.

       While  a	 message  is  in  the  transmit	 queue	its  payload bytes are
       accounted for.  If an attempt is made to send a message while there  is
       not  sufficient	room on the transmit queue, the call will either block
       or return EAGAIN.

       Trying to send to a destination that is marked congested	 (see  above),
       the call will either block or return ENOBUFS.

       A  message sent with no payload bytes will not consume any space in the
       destination's send buffer but will result in a message receipt  on  the
       destination.  The  receiver  will  not get any payload data but will be
       able to see the sender's address.

       Messages sent to a port to which no socket is bound  will  be  silently
       discarded  by  the  destination host. No error messages are reported to
       the sender.

   Message Receipt
       Messages may be received with recvmsg(2) on an RDS socket  once	it  is
       bound to a source address. RDS will return messages in-order, i.e. mes‐
       sages from the same sender will arrive in the same order in which  they
       were be sent.

       The address of the sender will be returned in the sockaddr_in structure
       pointed to by the msg_name field, if set.

       If the MSG_PEEK flag is given, the first	 message  on  the  receive  is
       returned without removing it from the queue.

       The memory consumed by messages waiting for delivery does not limit the
       number of messages that can be queued for receive. RDS does attempt  to
       perform congestion control as described in the section above.

       If the length of the message exceeds the size of the buffer provided to
       recvmsg(2), then the remainder of the bytes in  the  message  are  dis‐
       carded  and  the	 MSG_TRUNC flag is set in the msg_flags field. In this
       truncating case recvmsg(2)  will	 still	return	the  number  of	 bytes
       copied,	not  the  length of entire messge.  If MSG_TRUNC is set in the
       flags argument to recvmsg(2), then it will return the number  of	 bytes
       in  the	entire message. Thus one can examine the size of the next mes‐
       sage in the receive queue without incurring a copying overhead by  pro‐
       viding  a  zero length buffer and setting MSG_PEEK and MSG_TRUNC in the
       flags argument.

       The sending address of a zero-length message will still be provided  in
       the msg_name field.

   Control Messages
       RDS  uses control messages (a.k.a. ancillary data) through the msg_con‐
       trol and msg_controllen fields in sendmsg(2) and	 recvmsg(2).   Control
       messages	 generated  by	RDS  have a cmsg_level value of sol_rds.  Most
       control messages are related to the zerocopy  interface	added  in  RDS
       version 3, and are described in rds-rdma(7).

       The  only  exception  is	 the  RDS_CMSG_CONG_UPDATE  message,  which is
       described in the following section.

   Polling
       RDS supports the poll(2) interface in a	limited	 fashion.   POLLIN  is
       returned	 when  there  is  a message (either a proper RDS message, or a
       control message) waiting in the socket's	 receive  queue.   POLLOUT  is
       always returned while there is room on the socket's send queue.

       Sending	to congested ports requires special handling. When an applica‐
       tion tries to send to a congested destination,  the  system  call  will
       return ENOBUFS.	However, it cannot poll for POLLOUT, as there is prob‐
       ably still room on the transmit queue, so the  call  to	poll(2)	 would
       return immediately, even though the destination is still congested.

       There are two ways of dealing with this situation. The first is to sim‐
       ply poll for POLLIN.  By default, a  process  sleeping  in  poll(2)  is
       always woken up when the congestion map is updated, and thus the appli‐
       cation can retry any previously congested sends.

       The second option is explicit congestion monitoring,  which  gives  the
       application more fine-grained control.

       With  explicit  monitoring, the application polls for POLLIN as before,
       and additionally uses the RDS_CONG_MONITOR socket option to  install  a
       64bit  mask  value in the socket, where each bit corresponds to a group
       of ports. When a congestion update arrives, RDS checks the set of ports
       that  became  uncongested against the bit mask installed in the socket.
       If they overlap, a control messages is enqueued on the socket, and  the
       application is woken up. When it calls recvmsg(2), it will be given the
       control message containing the bitmap.  on the socket.

       The congestion monitor bitmask can be set and  queried  using  setsock‐
       opt(2) with RDS_CONG_MONITOR, and a pointer to the 64bit mask variable.

       Congestion   updates   are   delivered	to   the    application	   via
       RDS_CMSG_CONG_UPDATE  control  messages.	 These	control	 messages  are
       always delivered by themselves (or  possibly  additional	 control  mes‐
       sages), but never along with a RDS data message. The cmsg_data field of
       the control message is an 8 byte datum containing the 64bit mask value.

       Applications  can  use the following macros to test for and set bits in
       the bitmask:

       #define RDS_CONG_MONITOR_SIZE   64
       #define RDS_CONG_MONITOR_BIT(port)  (((unsigned int) port) % RDS_CONG_MONITOR_SIZE)
       #define RDS_CONG_MONITOR_MASK(port) (1 << RDS_CONG_MONITOR_BIT(port))


   Canceling Messages
       An application can cancel (flush) messages from the  send  queue	 using
       the  RDS_CANCEL_SENT_TO	socket	option	with setsockopt(2).  This call
       takes an optional sockaddr_in address structure as argument. If	given,
       only  messages  to  the	destination specified by this address are dis‐
       carded. If no address is given, all pending messages are discarded.

       Note that this affects messages that have not yet been  transmitted  as
       well  as messages that have been transmitted, but for which no acknowl‐
       edgment from the remote host has been received yet.

   Reliability
       If sendmsg(2) succeeds, RDS guarantees that the	message	 will  be vis‐
       ible   to  recvmsg(2)  on  a socket bound to the destination address as
       long as that destination socket remains open.

       If there is no socket bound on  the   destination,   the	  message   is
       silently	 dropped.   If	the sending RDS can't be sure that there is no
       socket bound then it will try to send the message indefinitely until it
       can be sure or the sent message is canceled.

       If  a socket is closed then all pending sent messages on the socket are
       canceled and may or may not be seen by the receiver.

       The RDS_CANCEL_SENT_TO socket option can be used to cancel all  pending
       messages to a given destination.

       If  a  receiving socket is closed with pending messages then the sender
       considers those messages as  having  left  the  network and  will   not
       retransmit them.

       A   message  will  only be seen by recvmsg(2) once, unless MSG_PEEK was
       specified. Once the message has been delivered it is removed  from  the
       sending socket's transmit queue.

       All  messages sent from the same socket to the same destination will be
       delivered in the order they're sent. Messages sent from different sock‐
       ets, or to different destinations, may be delivered in any order.

SYSCTL VALUES
       These   parameteres  may	 only  be  accessed  through  their  files  in
       /proc/sys/net/rds.  Access through sysctl(2) is not supported.

       pf_rds This file contains the string  representation  of	 the  protocol
	      family  constant passed to socket(2) to create a new RDS socket.

       sol_rds
	      This file contains the string representation of the socket level
	      parameter	 that  is passed to getsockopt(2) and setsockopt(2) to
	      manipulate RDS socket options.

       max_unacked_bytes and max_unacked_packets
	      These parameters are used to tune the generation of acknowledge‐
	      ments.  By  default,  the system receiving RDS messages does not
	      send back explicit acknowledgements unless it transmits  a  mes‐
	      sage  of	its own (in which case the ACK is piggybacked onto the
	      outgoing message), or when the sending system requests an ACK.

	      However, the sender needs to see an ACK from  time  to  time  so
	      that  it can purge old messages from the send queue. The unacked
	      bytes and packet counters are used to keep  track	 of  how  much
	      data  has been sent without requesting an ACK. The default is to
	      request an acknowledgement every 16 packets,  or	every  16  MB,
	      whichever comes first.

       reconnect_delay_min_ms and reconnect_delay_max_ms
	      RDS  uses	 host-to-host  connections  to	transport RDS messages
	      (both for the TCP and the Infiniband transport). If this connec‐
	      tion  breaks,  RDS  will	try  to	 re-establish  the connection.
	      Because this reconnect may be triggered by  both	hosts  at  the
	      same  time and fail, RDS uses a random backoff before attempting
	      a reconnect. These two parameters specify the minimum and	 maxi‐
	      mum  delay  in  milliseconds. The default values are 1 and 1000,
	      respectively.

SEE ALSO
       rds-rdma(7), socket(2), bind(2), sendmsg(2), recvmsg(2), getsockopt(2),
       setsockopt(2).



									RDS(7)
