## 原始press用户手册,组织结构,如下
``` 文件树：B75D104
|-- B75D104/
    |-- 00-转发与控制分离业务/
        |-- 01-转发与控制分离系统概述/
            |-- 转发与控制分离系统概述命令.json
            |-- 转发与控制分离系统概述配置.json
        |-- 02-CP-UP连接管理/
            |-- CP-UP连接管理Debug.json
            |-- CP-UP连接管理命令.json
            |-- CP-UP连接管理配置.json
        |-- 03-RMDB/
            |-- RMDB Debug.json
            |-- RMDB命令.json
            |-- RMDB配置.json
        |-- 04-弹性伸缩/
            |-- 弹性伸缩Debug.json
            |-- 弹性伸缩命令.json
            |-- 弹性伸缩配置.json
        |-- 05-vUP弹性伸缩/
            |-- vUP弹性伸缩命令.json
            |-- vUP弹性伸缩配置.json
        |-- 06-VM冲突检测/
            |-- VM冲突检测命令.json
            |-- VM冲突检测配置.json
        |-- 07-CP灾备/
            |-- CP灾备Debug.json
            |-- CP灾备命令.json
            |-- CP灾备配置.json
        |-- 08-UP备份/
            |-- UP备份Debug.json
            |-- UP备份命令.json
            |-- UP备份配置.json
        |-- 09-VM内部通信链路OAM/
            |-- VM内部通信链路OAM Debug.json
            |-- VM内部通信链路OAM命令.json
            |-- VM内部通信链路OAM配置.json
        |-- 10-VM内部通信链路Path MTU探测/
            |-- VM内部通信链路Path MTU探测Debug.json
            |-- VM内部通信链路Path MTU探测命令.json
            |-- VM内部通信链路Path MTU探测配置.json
        |-- 11-防脑裂/
            |-- 防脑裂Debug.json
            |-- 防脑裂命令.json
            |-- 防脑裂配置.json
        |-- 12-CP内部协议报文流量控制/
            |-- CP内部协议报文流量控制命令.json
            |-- CP内部协议报文流量控制配置.json
        |-- 13-CP内部流量负载分担/
            |-- CP内部流量负载分担命令.json
            |-- CP内部流量负载分担配置.json
        |-- 14-ALR/
            |-- ALR Debug.json
            |-- ALR命令.json
            |-- ALR配置.json
        |-- 15-系统异常检测和虚机自愈/
            |-- 系统异常检测和虚机自愈Debug.json
            |-- 系统异常检测和虚机自愈命令.json
            |-- 系统异常检测和虚机自愈配置.json
        |-- 16-UP管理组/
            |-- UP管理组命令.json
            |-- UP管理组配置.json
        |-- 17-基于驱动的攻击防范/
            |-- 基于驱动的攻击防范命令.json
            |-- 基于驱动的攻击防范配置.json
    |-- 01-基础配置/
        |-- 01-CLI/
            |-- CLI命令.json
            |-- CLI配置.json
        |-- 02-RBAC/
            |-- RBAC Debug.json
            |-- RBAC命令.json
            |-- RBAC配置.json
        |-- 03-登录设备/
            |-- 登录设备Debug.json
            |-- 登录设备命令.json
            |-- 登录设备配置.json
        |-- 04-FTP和TFTP/
            |-- FTP Debug.json
            |-- FTP和TFTP命令.json
            |-- FTP和TFTP配置.json
        |-- 05-文件系统管理/
            |-- 文件系统管理命令.json
            |-- 文件系统管理配置.json
        |-- 06-配置文件管理/
            |-- 配置文件管理.json
            |-- 配置文件管理命令.json
        |-- 07-软件升级/
            |-- 软件升级命令.json
            |-- 软件升级配置.json
        |-- 08-ISSU/
            |-- ISSU Debug.json
            |-- ISSU命令.json
            |-- ISSU配置.json
        |-- 09-GIR/
            |-- GIR命令.json
            |-- GIR配置.json
        |-- 10-应急Shell/
            |-- 应急Shell命令.json
            |-- 应急Shell配置.json
        |-- 11-自动配置/
            |-- 自动配置.json
            |-- 自动配置命令.json
        |-- 12-预配置/
            |-- 预配置.json
            |-- 预配置命令.json
        |-- 13-目标配置管理/
            |-- 目标配置管理.json
            |-- 目标配置管理命令.json
        |-- 14-设备管理/
            |-- 设备管理命令.json
            |-- 设备管理配置.json
        |-- 15-安全域/
            |-- 安全域命令.json
            |-- 安全域配置.json
        |-- 16-Tcl/
            |-- Tcl命令.json
            |-- Tcl配置.json
        |-- 17-Python/
            |-- Python命令.json
            |-- Python配置.json
        |-- 18-License管理/
            |-- License管理命令.json
            |-- License管理配置.json
    |-- 02-虚拟化技术/
        |-- 01-IRF/
            |-- IRF Debug.json
            |-- IRF命令.json
            |-- IRF配置.json
        |-- 02-MDC/
            |-- MDC命令.json
            |-- MDC配置.json
        |-- 03-Context/
            |-- Context命令.json
            |-- Context配置.json
        |-- 04-IRF（星堆）/
            |-- IRF Debug（星堆）.json
            |-- IRF命令（星堆）.json
            |-- IRF配置（星堆）.json
    |-- 03-接口管理/
        |-- 01-接口批量配置/
            |-- 接口批量配置.json
            |-- 接口批量配置命令.json
        |-- 02-以太网接口/
            |-- 以太网接口Debug.json
            |-- 以太网接口命令.json
            |-- 以太网接口配置.json
        |-- 03-WAN接口/
            |-- WAN接口命令.json
            |-- WAN接口配置.json
        |-- 04-POS接口/
            |-- POS接口命令.json
            |-- POS接口配置.json
        |-- 05-CPOS接口/
            |-- CPOS接口命令.json
            |-- CPOS接口配置.json
        |-- 06-ATM接口/
            |-- ATM接口命令.json
            |-- ATM接口配置.json
        |-- 07-LoopBack、NULL和InLoopBack接口/
            |-- LoopBack接口、NULL接口和InLoopBack接口命令.json
            |-- LoopBack接口、NULL接口和InLoopBack接口配置.json
        |-- 08-FlexE接口/
            |-- FlexE接口命令.json
            |-- FlexE接口配置.json
    |-- 04-二层技术-以太网交换/
        |-- 01-MAC地址表/
            |-- MAC地址表Debug.json
            |-- MAC地址表命令.json
            |-- MAC地址表配置.json
        |-- 02-以太网链路聚合/
            |-- 以太网链路聚合Debug.json
            |-- 以太网链路聚合命令.json
            |-- 以太网链路聚合配置.json
        |-- 03-DRNI/
            |-- DRNI Debug.json
            |-- DRNI命令.json
            |-- DRNI配置.json
        |-- 04-端口隔离/
            |-- 端口隔离命令.json
            |-- 端口隔离配置.json
        |-- 05-VLAN/
            |-- VLAN命令.json
            |-- VLAN配置.json
        |-- 06-MVRP/
            |-- MVRP Debug.json
            |-- MVRP命令.json
            |-- MVRP配置.json
        |-- 07-QinQ/
            |-- QinQ命令.json
            |-- QinQ配置.json
        |-- 08-VLAN映射/
            |-- VLAN映射命令.json
            |-- VLAN映射配置.json
        |-- 09-VLAN终结/
            |-- VLAN终结Debug.json
            |-- VLAN终结命令.json
            |-- VLAN终结配置.json
        |-- 10-PBB/
            |-- PBB Debug.json
            |-- PBB命令.json
            |-- PBB配置.json
        |-- 11-环路检测/
            |-- 环路检测Debug.json
            |-- 环路检测命令.json
            |-- 环路检测配置.json
        |-- 12-生成树/
            |-- 生成树Debug.json
            |-- 生成树命令.json
            |-- 生成树配置.json
        |-- 13-LLDP/
            |-- LLDP Debug.json
            |-- LLDP命令.json
            |-- LLDP配置.json
        |-- 14-L2PT/
            |-- L2PT Debug.json
            |-- L2PT命令.json
            |-- L2PT配置.json
        |-- 15-业务环回组/
            |-- 业务环回组Debug.json
            |-- 业务环回组命令.json
            |-- 业务环回组配置.json
        |-- 16-二层转发/
            |-- 二层转发Debug.json
            |-- 二层转发命令.json
            |-- 二层转发配置.json
    |-- 05-二层技术-广域网接入/
        |-- 01-PPP/
            |-- PPP Debug.json
            |-- PPP命令.json
            |-- PPP配置.json
        |-- 02-L2TP/
            |-- L2TP Debug.json
            |-- L2TP命令.json
            |-- L2TP配置.json
        |-- 03-HDLC/
            |-- HDLC Debug.json
            |-- HDLC命令.json
            |-- HDLC配置.json
        |-- 04-ISDN/
            |-- ISDN Debug.json
            |-- ISDN命令.json
            |-- ISDN配置.json
        |-- 05-ATM/
            |-- ATM Debug.json
            |-- ATM命令.json
            |-- ATM配置.json
        |-- 06-Modem管理/
            |-- Modem管理Debug.json
            |-- Modem管理命令.json
            |-- Modem管理配置.json
        |-- 07-3G Modem和4G Modem管理/
            |-- 3G Modem和4G Modem管理Debug.json
            |-- 3G Modem和4G Modem管理命令.json
            |-- 3G Modem和4G Modem管理配置.json
        |-- 08-DDR/
            |-- DDR Debug.json
            |-- DDR命令.json
            |-- DDR配置.json
        |-- 09-ANCP/
            |-- ANCP Debug.json
            |-- ANCP命令.json
            |-- ANCP配置.json
        |-- 10-IPoE/
            |-- IPoE Debug.json
            |-- IPoE命令.json
            |-- IPoE配置.json
        |-- 11-帧中继/
            |-- 帧中继Debug.json
            |-- 帧中继命令.json
            |-- 帧中继配置.json
        |-- 12-OTN/
            |-- OTN命令.json
            |-- OTN配置.json
    |-- 06-终端接入/
        |-- 01-POS终端接入/
            |-- POS终端接入Debug.json
            |-- POS终端接入命令.json
            |-- POS终端接入配置.json
        |-- 02-RTC终端接入/
            |-- RTC终端接入Debug.json
            |-- RTC终端接入命令.json
            |-- RTC终端接入配置.json
    |-- 07-三层技术-IP业务/
        |-- 01-ARP/
            |-- ARP Debug.json
            |-- ARP命令.json
            |-- ARP配置.json
        |-- 02-IP地址/
            |-- IP地址 Debug.json
            |-- IP地址命令.json
            |-- IP地址配置.json
        |-- 03-DHCP/
            |-- DHCP Debug.json
            |-- DHCP命令.json
            |-- DHCP用户下线原因.json
            |-- DHCP配置.json
        |-- 04-域名解析/
            |-- 域名解析Debug.json
            |-- 域名解析命令.json
            |-- 域名解析配置.json
        |-- 05-mDNS中继/
            |-- mDNS中继Debug.json
            |-- mDNS中继命令.json
            |-- mDNS中继配置.json
        |-- 06-NAT/
            |-- NAT Debug.json
            |-- NAT命令.json
            |-- NAT配置.json
        |-- 07-IP转发基础/
            |-- IP转发基础Debug.json
            |-- IP转发基础命令.json
            |-- IP转发基础配置.json
        |-- 08-快速转发/
            |-- 快速转发命令.json
            |-- 快速转发配置.json
        |-- 09-多CPU报文负载分担/
            |-- 多CPU报文负载分担命令.json
            |-- 多CPU报文负载分担配置.json
        |-- 10-邻接表/
            |-- 邻接表命令.json
            |-- 邻接表配置.json
        |-- 11-IRDP/
            |-- IRDP命令.json
            |-- IRDP配置.json
        |-- 12-IP性能优化/
            |-- IP性能优化Debug.json
            |-- IP性能优化命令.json
            |-- IP性能优化配置.json
        |-- 13-UDP Helper/
            |-- UDP Helper Debug.json
            |-- UDP Helper命令.json
            |-- UDP Helper配置.json
        |-- 14-IPv6基础/
            |-- IPv6基础Debug.json
            |-- IPv6基础命令.json
            |-- IPv6基础配置.json
        |-- 15-DHCPv6/
            |-- DHCPv6 Debug.json
            |-- DHCPv6命令.json
            |-- DHCPv6配置.json
        |-- 16-IPv6快速转发/
            |-- IPv6快速转发命令.json
            |-- IPv6快速转发配置.json
        |-- 17-AFT/
            |-- AFT Debug.json
            |-- AFT命令.json
            |-- AFT配置.json
        |-- 18-隧道/
            |-- 隧道Debug.json
            |-- 隧道命令.json
            |-- 隧道配置.json
        |-- 19-GRE/
            |-- GRE Debug.json
            |-- GRE命令.json
            |-- GRE配置.json
        |-- 20-ADVPN/
            |-- ADVPN Debug.json
            |-- ADVPN命令.json
            |-- ADVPN配置.json
        |-- 21-WAAS/
            |-- WAAS Debug.json
            |-- WAAS命令.json
            |-- WAAS配置.json
        |-- 22-HTTP重定向/
            |-- HTTP重定向Debug.json
            |-- HTTP重定向命令.json
            |-- HTTP重定向配置.json
        |-- 23-Lighttpd Web服务/
            |-- Lighttpd Web服务命令.json
            |-- Lighttpd Web服务配置.json
        |-- 24-V2V/
            |-- V2V Debug.json
            |-- V2V命令.json
            |-- V2V配置.json
    |-- 08-三层技术-IP路由/
        |-- 01-IP路由基础/
            |-- IP路由基础Debug.json
            |-- IP路由基础命令.json
            |-- IP路由基础配置.json
        |-- 02-静态路由/
            |-- 静态路由Debug.json
            |-- 静态路由命令.json
            |-- 静态路由配置.json
        |-- 03-RIP/
            |-- RIP Debug.json
            |-- RIP命令.json
            |-- RIP配置.json
        |-- 04-OSPF/
            |-- OSPF Debug.json
            |-- OSPF命令.json
            |-- OSPF配置.json
        |-- 05-IS-IS/
            |-- IS-IS Debug.json
            |-- IS-IS命令.json
            |-- IS-IS配置.json
        |-- 06-EIGRP/
            |-- EIGRP Debug.json
            |-- EIGRP命令.json
            |-- EIGRP配置.json
        |-- 07-BGP/
            |-- BGP Debug.json
            |-- BGP命令.json
            |-- BGP配置.json
        |-- 08-策略路由/
            |-- 策略路由Debug.json
            |-- 策略路由命令.json
            |-- 策略路由配置.json
        |-- 09-IPv6静态路由/
            |-- IPv6静态路由Debug.json
            |-- IPv6静态路由命令.json
            |-- IPv6静态路由配置.json
        |-- 10-RIPng/
            |-- RIPng Debug.json
            |-- RIPng命令.json
            |-- RIPng配置.json
        |-- 11-OSPFv3/
            |-- OSPFv3 Debug.json
            |-- OSPFv3命令.json
            |-- OSPFv3配置.json
        |-- 12-IPv6策略路由/
            |-- IPv6策略路由Debug.json
            |-- IPv6策略路由命令.json
            |-- IPv6策略路由配置.json
        |-- 13-路由策略/
            |-- 路由策略Debug.json
            |-- 路由策略命令.json
            |-- 路由策略配置.json
        |-- 14-MTR/
            |-- MTR命令.json
            |-- MTR配置.json
        |-- 15-DCN/
            |-- DCN命令.json
            |-- DCN配置.json
    |-- 09-IP组播/
        |-- 01-组播概述/
            |-- 组播概述.json
        |-- 02-IGMP Snooping/
            |-- IGMP Snooping Debug.json
            |-- IGMP Snooping命令.json
            |-- IGMP Snooping配置.json
        |-- 03-PIM Snooping/
            |-- PIM Snooping命令.json
            |-- PIM Snooping配置.json
        |-- 04-组播VLAN/
            |-- 组播VLAN命令.json
            |-- 组播VLAN配置.json
        |-- 05-组播路由与转发/
            |-- 组播路由与转发Debug.json
            |-- 组播路由与转发命令.json
            |-- 组播路由与转发配置.json
        |-- 06-IGMP/
            |-- IGMP Debug.json
            |-- IGMP命令.json
            |-- IGMP配置.json
        |-- 07-PIM/
            |-- PIM Debug.json
            |-- PIM命令.json
            |-- PIM配置.json
        |-- 08-MSDP/
            |-- MSDP Debug.json
            |-- MSDP命令.json
            |-- MSDP配置.json
        |-- 09-组播VPN概述/
            |-- 组播VPN Debug.json
            |-- 组播VPN命令.json
            |-- 组播VPN概述.json
        |-- 10-MDT模式MVPN/
            |-- MDT模式MVPN配置.json
        |-- 11-RSVP-TE模式MVPN/
            |-- RSVP-TE模式MVPN配置.json
        |-- 12-mLDP模式MVPN/
            |-- mLDP模式MVPN配置.json
        |-- 13-BIER模式MVPN/
            |-- BIER模式MVPN配置.json
        |-- 14-跨VPN组播转发/
            |-- 跨VPN组播转发配置.json
        |-- 15-MLD Snooping/
            |-- MLD Snooping Debug.json
            |-- MLD Snooping命令.json
            |-- MLD Snooping配置.json
        |-- 16-IPv6 PIM Snooping/
            |-- IPv6 PIM Snooping命令.json
            |-- IPv6 PIM Snooping配置.json
        |-- 17-IPv6组播VLAN/
            |-- IPv6组播VLAN命令.json
            |-- IPv6组播VLAN配置.json
        |-- 18-IPv6组播路由与转发/
            |-- IPv6组播路由与转发Debug.json
            |-- IPv6组播路由与转发命令.json
            |-- IPv6组播路由与转发配置.json
        |-- 19-MLD/
            |-- MLD Debug.json
            |-- MLD命令.json
            |-- MLD配置.json
        |-- 20-IPv6 PIM/
            |-- IPv6 PIM Debug.json
            |-- IPv6 PIM命令.json
            |-- IPv6 PIM配置.json
    |-- 10-BIER/
        |-- 01-BIER/
            |-- BIER Debug.json
            |-- BIER命令.json
            |-- BIER配置.json
        |-- 02-BIER OAM/
            |-- BIER OAM命令.json
            |-- BIER OAM配置.json
    |-- 11-MPLS/
        |-- 01-MPLS基础/
            |-- MPLS基础Debug.json
            |-- MPLS基础命令.json
            |-- MPLS基础配置.json
        |-- 02-静态LSP/
            |-- 静态LSP Debug.json
            |-- 静态LSP命令.json
            |-- 静态LSP配置.json
        |-- 03-LDP/
            |-- LDP Debug.json
            |-- LDP命令.json
            |-- LDP配置.json
        |-- 04-MPLS TE/
            |-- MPLS TE Debug.json
            |-- MPLS TE命令.json
            |-- MPLS TE配置.json
        |-- 05-静态CRLSP/
            |-- 静态CRLSP Debug.json
            |-- 静态CRLSP命令.json
            |-- 静态CRLSP配置.json
        |-- 06-RSVP/
            |-- RSVP Debug.json
            |-- RSVP命令.json
            |-- RSVP配置.json
        |-- 07-隧道策略/
            |-- 隧道策略命令.json
            |-- 隧道策略配置.json
        |-- 08-MPLS L3VPN/
            |-- MPLS L3VPN Debug.json
            |-- MPLS L3VPN命令.json
            |-- MPLS L3VPN配置.json
            |-- MPLS L3VPN配置举例.json
        |-- 09-IPv6 MPLS L3VPN/
            |-- IPv6 MPLS L3VPN Debug.json
            |-- IPv6 MPLS L3VPN命令.json
            |-- IPv6 MPLS L3VPN配置.json
            |-- IPv6 MPLS L3VPN配置举例.json
        |-- 10-MPLS L2VPN/
            |-- MPLS L2VPN Debug.json
            |-- MPLS L2VPN命令.json
            |-- MPLS L2VPN配置.json
        |-- 11-VPLS/
            |-- VPLS命令.json
            |-- VPLS配置.json
        |-- 12-L2VPN接入L3VPN或IP骨干网/
            |-- L2VPN接入L3VPN或IP骨干网 Debug.json
            |-- L2VPN接入L3VPN或IP骨干网命令.json
            |-- L2VPN接入L3VPN或IP骨干网配置.json
        |-- 13-MPLS OAM/
            |-- MPLS OAM Debug.json
            |-- MPLS OAM命令.json
            |-- MPLS OAM配置.json
        |-- 14-MPLS保护倒换/
            |-- MPLS保护倒换Debug.json
            |-- MPLS保护倒换命令.json
            |-- MPLS保护倒换配置.json
        |-- 15-MCE/
            |-- MCE命令.json
            |-- MCE配置.json
    |-- 12-Segment Routing/
        |-- 01-SR-MPLS/
            |-- SR-MPLS命令.json
            |-- SR-MPLS配置.json
        |-- 02-SR-MPLS TE Policy/
            |-- SR-MPLS TE Policy命令.json
            |-- SR-MPLS TE Policy配置.json
        |-- 03-SRv6/
            |-- SRv6 Debug.json
            |-- SRv6命令.json
            |-- SRv6配置.json
        |-- 04-SRv6 TE Policy/
            |-- SRv6 TE Policy命令.json
            |-- SRv6 TE Policy配置.json
        |-- 05-SRv6 VPN概述/
            |-- SRv6 VPN命令.json
            |-- SRv6 VPN概述.json
        |-- 06-IP L3VPN over SRv6/
            |-- IP L3VPN over SRv6配置.json
        |-- 07-EVPN L3VPN over SRv6/
            |-- EVPN L3VPN over SRv6配置.json
        |-- 08-EVPN VPWS over SRv6/
            |-- EVPN VPWS over SRv6配置.json
        |-- 09-EVPN VPLS over SRv6/
            |-- EVPN VPLS over SRv6配置.json
        |-- 10-公网IP over SRv6/
            |-- 公网IP over SRv6配置.json
        |-- 11-SRv6 OAM/
            |-- SRv6 OAM命令.json
            |-- SRv6 OAM配置.json
        |-- 12-SRv6网络切片/
            |-- SRv6网络切片命令.json
            |-- SRv6网络切片配置.json
        |-- 13-SRv6 SFC/
            |-- SRv6 SFC命令.json
            |-- SRv6 SFC配置.json
    |-- 13-ACL和QoS/
        |-- 01-ACL/
            |-- ACL Debug.json
            |-- ACL命令.json
            |-- ACL配置.json
        |-- 02-QoS/
            |-- QoS命令.json
            |-- QoS配置.json
        |-- 03-MPLS QoS/
            |-- MPLS QoS命令.json
            |-- MPLS QoS配置.json
        |-- 04-帧中继QoS/
            |-- 帧中继QoS命令.json
            |-- 帧中继QoS配置.json
        |-- 05-HQoS/
            |-- HQoS命令.json
            |-- HQoS配置.json
        |-- 06-数据缓冲区/
            |-- 数据缓冲区命令.json
            |-- 数据缓冲区配置.json
        |-- 07-时间段/
            |-- 时间段命令.json
            |-- 时间段配置.json
        |-- 08-QCN/
            |-- QCN Debug.json
            |-- QCN命令.json
            |-- QCN配置.json
        |-- 09-Flowspec/
            |-- Flowspec Debug.json
            |-- Flowspec命令.json
            |-- Flowspec配置.json
    |-- 14-安全/
        |-- 01-UCM/
            |-- UCM Debug.json
            |-- UCM命令.json
            |-- UCM配置.json
        |-- 02-AAA/
            |-- AAA Debug.json
            |-- AAA命令.json
            |-- AAA配置.json
        |-- 03-802.1X（三层）/
            |-- 802.1X Debug（三层）.json
            |-- 802.1X命令（三层）.json
            |-- 802.1X配置（三层）.json
        |-- 03-802.1X（二层）/
            |-- 802.1X Debug（二层）.json
            |-- 802.1X命令（二层）.json
            |-- 802.1X配置（二层）.json
        |-- 04-MAC地址认证/
            |-- MAC地址认证Debug.json
            |-- MAC地址认证命令.json
            |-- MAC地址认证配置.json
        |-- 05-Portal/
            |-- Portal Debug.json
            |-- Portal命令.json
            |-- Portal配置.json
        |-- 06-端口安全/
            |-- 端口安全Debug.json
            |-- 端口安全命令.json
            |-- 端口安全配置.json
        |-- 07-DAE代理/
            |-- DAE代理Debug.json
            |-- DAE代理命令.json
            |-- DAE代理配置.json
        |-- 08-用户身份识别与管理/
            |-- 用户身份识别与管理Debug.json
            |-- 用户身份识别与管理配置.json
            |-- 用户身份识别和管理命令.json
        |-- 09-User Profile/
            |-- User Profile Debug.json
            |-- User Profile命令.json
            |-- User Profile配置.json
        |-- 10-Password Control/
            |-- Password Control命令.json
            |-- Password Control配置.json
        |-- 11-keychain/
            |-- keychain Debug.json
            |-- keychain命令.json
            |-- keychain配置.json
        |-- 12-Portal代理/
            |-- Portal代理Debug.json
            |-- Portal代理命令.json
            |-- Portal代理配置.json
        |-- 13-公钥管理/
            |-- 公钥管理命令.json
            |-- 公钥管理配置.json
        |-- 14-PKI/
            |-- PKI Debug.json
            |-- PKI命令.json
            |-- PKI配置.json
        |-- 15-IPsec/
            |-- IPsec Debug.json
            |-- IPsec命令.json
            |-- IPsec配置.json
        |-- 16-Group Domain VPN/
            |-- Group Domain VPN Debug.json
            |-- Group Domain VPN命令.json
            |-- Group Domain VPN配置.json
        |-- 17-SSH/
            |-- SSH Debug.json
            |-- SSH命令.json
            |-- SSH配置.json
        |-- 18-SSL/
            |-- SSL命令.json
            |-- SSL配置.json
        |-- 19-SSL VPN/
            |-- SSL VPN Debug.json
            |-- SSL VPN命令.json
            |-- SSL VPN配置.json
        |-- 20-ASPF/
            |-- ASPF Debug.json
            |-- ASPF命令.json
            |-- ASPF配置.json
        |-- 21-APR/
            |-- APR命令.json
            |-- APR配置.json
        |-- 22-会话管理/
            |-- 会话管理Debug.json
            |-- 会话管理命令.json
            |-- 会话管理配置.json
        |-- 23-连接数限制/
            |-- 连接数限制Debug.json
            |-- 连接数限制命令.json
            |-- 连接数限制配置.json
        |-- 24-对象组/
            |-- 对象组命令.json
            |-- 对象组配置.json
        |-- 25-对象策略/
            |-- 对象策略Debug.json
            |-- 对象策略命令.json
            |-- 对象策略配置.json
        |-- 26-攻击检测与防范/
            |-- 攻击检测与防范Debug.json
            |-- 攻击检测与防范命令.json
            |-- 攻击检测与防范配置.json
        |-- 27-基于IP的攻击防御/
            |-- 基于IP的攻击防御命令.json
            |-- 基于IP的攻击防御配置.json
        |-- 28-IP Source Guard/
            |-- IP Source Guard Debug.json
            |-- IP Source Guard命令.json
            |-- IP Source Guard配置.json
        |-- 29-ARP攻击防御/
            |-- ARP攻击防御Debug.json
            |-- ARP攻击防御命令.json
            |-- ARP攻击防御配置.json
        |-- 30-ND攻击防御/
            |-- ND攻击防御Debug.json
            |-- ND攻击防御命令.json
            |-- ND攻击防御配置.json
        |-- 31-uRPF/
            |-- uRPF Debug.json
            |-- uRPF命令.json
            |-- uRPF配置.json
        |-- 32-SAVI/
            |-- SAVI命令.json
            |-- SAVI配置.json
        |-- 33-SAVA/
            |-- SAVA Debug.json
            |-- SAVA命令.json
            |-- SAVA配置.json
        |-- 34-SAVA-P/
            |-- SAVA-P Debug.json
            |-- SAVA-P命令.json
            |-- SAVA-P配置.json
        |-- 35-SAVNET/
            |-- SAVNET Debug.json
            |-- SAVNET命令.json
            |-- SAVNET配置.json
        |-- 36-MFF/
            |-- MFF Debug.json
            |-- MFF命令.json
            |-- MFF配置.json
        |-- 37-加密引擎/
            |-- 加密引擎Debug.json
            |-- 加密引擎命令.json
            |-- 加密引擎配置.json
        |-- 38-FIPS/
            |-- FIPS命令.json
            |-- FIPS配置.json
        |-- 39-MACsec/
            |-- MACsec Debug.json
            |-- MACsec命令.json
            |-- MACsec配置.json
        |-- 40-SMA/
            |-- SMA Debug.json
            |-- SMA命令.json
            |-- SMA配置.json
        |-- 41-加密口/
            |-- 加密口命令.json
            |-- 加密口配置.json
        |-- 42-信任等级/
            |-- 信任等级命令.json
            |-- 信任等级配置.json
        |-- 43-CSG/
            |-- CSG命令.json
            |-- CSG配置.json
        |-- 44-iSec/
            |-- iSec命令.json
            |-- iSec配置.json
    |-- 15-语音/
        |-- 01-语音用户线/
            |-- 语音用户线Debug.json
            |-- 语音用户线命令.json
            |-- 语音用户线配置.json
        |-- 02-语音实体/
            |-- 语音实体命令.json
            |-- 语音实体配置.json
        |-- 03-拨号策略/
            |-- 拨号策略Debug.json
            |-- 拨号策略命令.json
            |-- 拨号策略配置.json
        |-- 04-SIP/
            |-- SIP Debug.json
            |-- SIP命令.json
            |-- SIP配置.json
        |-- 05-语音业务/
            |-- 语音业务Debug.json
            |-- 语音业务命令.json
            |-- 语音业务配置.json
        |-- 06-Fax over IP/
            |-- Fax over IP命令.json
            |-- Fax over IP配置.json
        |-- 07-SRST/
            |-- SRST命令.json
            |-- SRST配置.json
        |-- 08-可定制IVR/
            |-- 可定制IVR Debug.json
            |-- 可定制IVR命令.json
            |-- 可定制IVR配置.json
        |-- 09-语音/
            |-- 语音Debug.json
    |-- 16-可靠性/
        |-- 01-接口备份/
            |-- 接口备份Debug.json
            |-- 接口备份命令.json
            |-- 接口备份配置.json
        |-- 02-以太网OAM/
            |-- 以太网OAM Debug.json
            |-- 以太网OAM命令.json
            |-- 以太网OAM配置.json
        |-- 03-CFD/
            |-- CFD Debug.json
            |-- CFD命令.json
            |-- CFD配置.json
        |-- 04-DLDP/
            |-- DLDP Debug.json
            |-- DLDP命令.json
            |-- DLDP配置.json
        |-- 05-RPR/
            |-- RPR Debug.json
            |-- RPR命令.json
            |-- RPR配置.json
        |-- 06-RRPP/
            |-- RRPP Debug.json
            |-- RRPP命令.json
            |-- RRPP配置.json
        |-- 07-ERPS/
            |-- ERPS Debug.json
            |-- ERPS命令.json
            |-- ERPS配置.json
        |-- 08-Smart Link/
            |-- Smart Link Debug.json
            |-- Smart Link命令.json
            |-- Smart Link配置.json
        |-- 09-Monitor Link/
            |-- Monitor Link Debug.json
            |-- Monitor Link命令.json
            |-- Monitor Link配置.json
        |-- 10-S-Trunk/
            |-- S-Trunk Debug.json
            |-- S-Trunk命令.json
            |-- S-Trunk配置.json
        |-- 11-误码检测/
            |-- 误码检测命令.json
            |-- 误码检测配置.json
        |-- 12-VRRP/
            |-- VRRP Debug.json
            |-- VRRP命令.json
            |-- VRRP配置.json
        |-- 13-多机备份/
            |-- 多机备份Debug.json
            |-- 多机备份命令.json
            |-- 多机备份配置.json
        |-- 14-备份组/
            |-- 备份组命令.json
            |-- 备份组配置.json
        |-- 15-业务实例组/
            |-- 业务实例组命令.json
            |-- 业务实例组配置.json
        |-- 16-冗余备份/
            |-- 冗余备份命令.json
            |-- 冗余备份配置.json
        |-- 20-BFD/
            |-- BFD Debug.json
            |-- BFD命令.json
            |-- BFD配置.json
        |-- 21-Track/
            |-- Track Debug.json
            |-- Track命令.json
            |-- Track配置.json
        |-- 22-进程分布优化/
            |-- 进程分布优化命令.json
            |-- 进程分布优化配置.json
        |-- 23-负载均衡/
            |-- 负载均衡Debug.json
            |-- 负载均衡命令.json
            |-- 负载均衡配置.json
    |-- 17-网络管理和监控/
        |-- 01-系统维护与调试/
            |-- 系统维护与调试命令.json
            |-- 系统维护与调试配置.json
        |-- 02-NQA/
            |-- NQA Debug.json
            |-- NQA命令.json
            |-- NQA配置.json
        |-- 03-iNQA/
            |-- iNQA Debug.json
            |-- iNQA命令.json
            |-- iNQA配置.json
        |-- 04-iFIT/
            |-- iFIT Debug.json
            |-- iFIT命令.json
            |-- iFIT配置.json
        |-- 05-SRPM/
            |-- SRPM Debug.json
            |-- SRPM命令.json
            |-- SRPM配置.json
        |-- 06-NTP/
            |-- NTP Debug.json
            |-- NTP命令.json
            |-- NTP配置.json
        |-- 07-PTP/
            |-- PTP Debug.json
            |-- PTP命令.json
            |-- PTP配置.json
        |-- 08-时钟同步/
            |-- 时钟同步Debug.json
            |-- 时钟同步命令.json
            |-- 时钟同步配置.json
        |-- 09-PoE/
            |-- PoE命令.json
            |-- PoE配置.json
        |-- 10-SNMP/
            |-- SNMP Debug.json
            |-- SNMP命令.json
            |-- SNMP配置.json
        |-- 11-RMON/
            |-- RMON Debug.json
            |-- RMON命令.json
            |-- RMON配置.json
        |-- 12-Event MIB/
            |-- Event MIB Debug.json
            |-- Event MIB命令.json
            |-- Event MIB配置.json
        |-- 13-NETCONF/
            |-- NETCONF Debug.json
            |-- NETCONF命令.json
            |-- NETCONF配置.json
        |-- 14-Puppet/
            |-- Puppet配置.json
        |-- 15-Chef/
            |-- Chef配置.json
        |-- 16-CWMP/
            |-- CWMP Debug.json
            |-- CWMP命令.json
            |-- CWMP配置.json
        |-- 17-EAA/
            |-- EAA命令.json
            |-- EAA配置.json
        |-- 18-进程监控和维护/
            |-- 进程监控和维护命令.json
            |-- 进程监控和维护配置.json
        |-- 19-Sampler/
            |-- Sampler命令.json
            |-- Sampler配置.json
        |-- 20-镜像/
            |-- 镜像命令.json
            |-- 镜像配置.json
        |-- 21-NetStream/
            |-- NetStream Debug.json
            |-- NetStream命令.json
            |-- NetStream配置.json
        |-- 22-IPv6 NetStream/
            |-- IPv6 NetStream Debug.json
            |-- IPv6 NetStream命令.json
            |-- IPv6 NetStream配置.json
        |-- 23-sFlow/
            |-- sFlow Debug.json
            |-- sFlow命令.json
            |-- sFlow配置.json
        |-- 24-TCP连接跟踪/
            |-- TCP连接跟踪命令.json
            |-- TCP连接跟踪配置.json
        |-- 25-性能管理/
            |-- 性能管理命令.json
            |-- 性能管理配置.json
        |-- 26-快速日志输出/
            |-- 快速日志输出命令.json
            |-- 快速日志输出配置.json
        |-- 27-Flow日志/
            |-- Flow日志命令.json
            |-- Flow日志配置.json
        |-- 28-信息中心/
            |-- 信息中心命令.json
            |-- 信息中心配置.json
        |-- 29-GOLD/
            |-- GOLD命令.json
            |-- GOLD配置.json
        |-- 30-Packet Capture/
            |-- Packet Capture命令.json
            |-- Packet Capture配置.json
        |-- 31-Flow-monitor/
            |-- Flow-monitor命令.json
            |-- Flow-monitor配置.json
        |-- 32-云平台连接/
            |-- 云平台连接Debug.json
            |-- 云平台连接命令.json
            |-- 云平台连接配置.json
        |-- 33-NetAnalysis/
            |-- NetAnalysis命令.json
            |-- NetAnalysis配置.json
    |-- 18-Telemetry/
        |-- 01-gRPC/
            |-- gRPC Debug.json
            |-- gRPC命令.json
            |-- gRPC配置.json
    |-- 19-确定性网络/
        |-- 01-DetNet/
            |-- DetNet命令.json
            |-- DetNet配置.json
        |-- 02-DetNetOAM/
            |-- DetNetOAM Debug.json
            |-- DetNetOAM命令.json
            |-- DetNetOAM配置.json
    |-- 20-OAA/
        |-- 01-OAP manager/
            |-- OAP Debug.json
            |-- OAP manager命令.json
            |-- OAP manager配置.json
        |-- 02-OAP单板/
            |-- OAP单板命令.json
            |-- OAP单板配置.json
    |-- 21-FC和FCoE/
        |-- 01-FC和FCoE/
            |-- FC和FCoE Debug.json
            |-- FC和FCoE命令.json
            |-- FC和FCoE配置.json
    |-- 22-TRILL/
        |-- 01-TRILL/
            |-- TRILL Debug.json
            |-- TRILL命令.json
            |-- TRILL配置.json
    |-- 23-SPB/
        |-- 01-SPBM/
            |-- SPBM Debug.json
            |-- SPBM命令.json
            |-- SPBM配置.json
    |-- 24-EVB/
        |-- 01-EVB/
            |-- EVB Debug.json
            |-- EVB命令.json
            |-- EVB配置.json
    |-- 25-EVI/
        |-- 01-EVI/
            |-- EVI Debug.json
            |-- EVI命令.json
            |-- EVI配置.json
    |-- 26-OpenFlow/
        |-- 01-OpenFlow/
            |-- OpenFlow Debug.json
            |-- OpenFlow命令.json
            |-- OpenFlow配置.json
    |-- 27-VXLAN/
        |-- 01-VXLAN/
            |-- VXLAN Debug.json
            |-- VXLAN命令.json
            |-- VXLAN配置.json
    |-- 28-EVPN/
        |-- 01-EVPN概述/
            |-- EVPN Debug.json
            |-- EVPN命令.json
            |-- EVPN概述.json
        |-- 02-EVPN VXLAN/
            |-- EVPN VXLAN配置.json
        |-- 03-EVPN VPLS/
            |-- EVPN VPLS配置.json
        |-- 04-EVPN VPWS/
            |-- EVPN VPWS配置.json
        |-- 05-EVPN L3VPN/
            |-- EVPN L3VPN配置.json
        |-- 06-EVPN数据中心互联/
            |-- EVPN数据中心互联配置.json
    |-- 29-NVGRE/
        |-- 01-NVGRE/
            |-- NVGRE命令.json
            |-- NVGRE配置.json
    |-- 30-NEMO/
        |-- 01-NEMO/
            |-- NEMO Debug.json
            |-- NEMO命令.json
            |-- NEMO配置.json
    |-- 31-LISP/
        |-- 01-LISP/
            |-- LISP Debug.json
            |-- LISP命令.json
            |-- LISP配置.json
    |-- 32-服务链/
        |-- 01-服务链/
            |-- 服务链Debug.json
            |-- 服务链命令.json
            |-- 服务链配置.json
    |-- 33-应用感知型网络/
        |-- 01-APN6/
            |-- APN6 Debug.json
            |-- APN6命令.json
            |-- APN6配置.json
        |-- 02-iBRAS业务感知/
            |-- iBRAS业务感知Debug.json
            |-- iBRAS业务感知命令.json
            |-- iBRAS业务感知配置.json
    |-- 34-AI智能运维/
        |-- AI智能运维Debug命令.json
        |-- AI智能运维命令.json
        |-- AI智能运维配置.json
    |-- 35-Probe命令/
        |-- 802.11 Probe命令.json
        |-- ACL Probe命令.json
        |-- AFT Probe命令.json
        |-- APN6 Probe命令.json
        |-- AP管理Probe命令.json
        |-- ARP Probe命令.json
        |-- ASPF Probe命令.json
        |-- BFD Probe命令.json
        |-- BGP Probe命令.json
        |-- BIER Probe命令.json
        |-- CFD Probe命令.json
        |-- Context Probe命令.json
        |-- CP-UP连接管理Probe.json
        |-- CP内部流量负载分担Probe命令.json
        |-- DBM Probe命令.json
        |-- DHCP Probe命令.json
        |-- DHCPv6 Probe命令.json
        |-- DLDP Probe命令.json
        |-- DRNI Probe命令.json
        |-- EIGRP Probe命令.json
        |-- EVB Probe命令.json
        |-- EVI Probe命令.json
        |-- EVPN Probe命令.json
        |-- FCoE Probe命令.json
        |-- FDB Probe命令.json
        |-- FIPS Probe命令.json
        |-- Flow Manager Probe命令.json
        |-- Flowspec Probe命令.json
        |-- Flow日志Probe命令.json
        |-- FPGA Probe命令.json
        |-- gRPC Probe命令.json
        |-- HA Probe命令.json
        |-- HTTPD Probe命令.json
        |-- ILOG Probe命令.json
        |-- IPCIM Probe命令.json
        |-- IPoE Probe命令.json
        |-- IPsec Probe命令.json
        |-- IPv6 IS-IS Probe命令.json
        |-- IPv6基础Probe命令.json
        |-- IPv6快速转发Probe命令.json
        |-- IPv6策略路由Probe命令.json
        |-- IPv6静态路由Probe命令.json
        |-- IP地址管理Probe命令.json
        |-- IP性能优化Probe命令.json
        |-- IP组播Probe命令.json
        |-- IP路由基础Probe命令.json
        |-- IP转发基础Probe命令.json
        |-- IRF Probe命令(星堆).json
        |-- IRF Probe命令.json
        |-- IS-IS Probe命令.json
        |-- KDNS Probe命令.json
        |-- keychain Probe命令.json
        |-- L2PT Probe命令.json
        |-- L2TP Probe命令.json
        |-- License管理Probe命令.json
        |-- LIPC Probe命令.json
        |-- LISP Probe命令.json
        |-- MACsec Probe.json
        |-- MAC地址表Probe命令.json
        |-- MBUF Probe命令.json
        |-- MDC Probe命令.json
        |-- MPLS L2VPN Probe命令.json
        |-- MPLS L3VPN Probe命令.json
        |-- MPLS TE Probe命令.json
        |-- MPLS保护倒换Probe命令.json
        |-- MPLS基础Probe命令.json
        |-- MTR Probe命令.json
        |-- MVRP Probe命令.json
        |-- NAT Probe命令.json
        |-- ND攻击防御Probe命令.json
        |-- NetStream Probe命令.json
        |-- NVGRE Probe命令.json
        |-- OpenFlow Probe命令.json
        |-- OSPF Probe命令.json
        |-- OSPFv3 Probe命令.json
        |-- Packet Capture Probe命令.json
        |-- Portal Probe命令.json
        |-- PPP Probe命令.json
        |-- PTP Probe命令.json
        |-- QoS Probe命令.json
        |-- RIP Probe命令.json
        |-- RIPng Probe命令.json
        |-- RLINK Probe命令.json
        |-- RMDB Probe命令.json
        |-- S-Trunk Probe命令.json
        |-- SAVA Probe命令.json
        |-- SAVA-P Probe命令.json
        |-- SAVNET Probe命令.json
        |-- sFlow Probe命令.json
        |-- SMA Probe命令.json
        |-- SNMP Probe命令.json
        |-- SR-MPLS Probe命令.json
        |-- SR-MPLS TE Policy Probe.json
        |-- SRPM Probe命令.json
        |-- SRv6 Probe命令.json
        |-- SRv6 TE Policy Probe命令.json
        |-- SRv6 VPN Probe.json
        |-- SRv6网络切片Probe命令.json
        |-- Track Probe命令.json
        |-- TRILL Probe命令.json
        |-- UCM Probe命令.json
        |-- UNICFG Probe命令.json
        |-- User Profile Probe命令.json
        |-- VLAN Probe命令.json
        |-- VM内部通信链路OAM Probe命令.json
        |-- VM管理Probe命令.json
        |-- VM组维护Probe命令.json
        |-- VPLS Probe命令.json
        |-- VRRP Probe命令.json
        |-- VXLAN Probe命令.json
        |-- WAAS Probe命令.json
        |-- WIPS Probe.json
        |-- WLAN IP Snooping Probe命令.json
        |-- WLAN Mesh Probe命令.json
        |-- WLAN RRM Probe命令.json
        |-- WLAN定位Probe命令.json
        |-- WLAN虚拟客户端Probe命令.json
        |-- WLAN负载均衡Probe命令.json
        |-- WLAN转发Probe.json
        |-- WLAN高可靠性Probe命令.json
        |-- 业务环回组Probe命令.json
        |-- 二层转发Probe命令.json
        |-- 云平台连接Probe命令.json
        |-- 以太网接口Probe命令.json
        |-- 以太网链路聚合Probe命令.json
        |-- 会话管理Probe命令.json
        |-- 信任等级Probe命令.json
        |-- 信息中心Probe命令.json
        |-- 公钥管理Probe命令.json
        |-- 内存Probe命令.json
        |-- 加密引擎Probe命令.json
        |-- 基于驱动的攻击防范Probe命令.json
        |-- 基础配置Probe命令.json
        |-- 备份组Probe命令.json
        |-- 多机备份Probe命令.json
        |-- 对象策略Probe命令.json
        |-- 对象组Probe命令.json
        |-- 快速日志输出Probe命令.json
        |-- 快速转发Probe命令.json
        |-- 接口管理Probe命令.json
        |-- 攻击检测与防范Probe.json
        |-- 生成树Probe命令.json
        |-- 登录设备Probe命令.json
        |-- 目标配置管理Probe命令.json
        |-- 策略路由Probe命令.json
        |-- 设备管理Probe命令.json
        |-- 负载均衡Probe命令.json
        |-- 进程监控和维护Prob命令.json
        |-- 邻接表Probe命令.json
        |-- 配置文件管理Probe命令.json
        |-- 配置管理Probe命令.json
        |-- 隧道Probe命令.json
        |-- 静态路由Probe命令.json
        |-- 频谱导航Probe命令.json
        |-- 驱动平台Probe.json
        |-- 驱动报文统计Probe命令.json
    |-- 36-诊断命令/
        |-- 802.1X诊断命令.json
        |-- ARP诊断命令.json
        |-- BGP诊断命令.json
        |-- BIER诊断命令.json
        |-- CP-UP连接管理诊断命令.json
        |-- CP灾备诊断命令.json
        |-- DBM诊断命令.json
        |-- DetNetOAM诊断命令.json
        |-- DHCPv6诊断命令.json
        |-- DHCP诊断命令.json
        |-- gRPC诊断命令.json
        |-- HA诊断命令.json
        |-- iFIT诊断命令.json
        |-- iNQA诊断命令.json
        |-- IPoE诊断命令.json
        |-- IP性能优化诊断命令.json
        |-- IP组播诊断命令.json
        |-- IP路由基础诊断命令.json
        |-- IS-IS诊断命令.json
        |-- iSec诊断命令.json
        |-- L2TP诊断命令.json
        |-- L2VPN诊断命令.json
        |-- LDP诊断命令.json
        |-- LIPC诊断命令.json
        |-- MBUF诊断命令.json
        |-- MDC诊断命令.json
        |-- MPLS诊断命令.json
        |-- NQA诊断命令.json
        |-- OSPF诊断命令.json
        |-- PPP诊断命令.json
        |-- PTP诊断命令.json
        |-- QoS诊断命令.json
        |-- SRPM诊断命令.json
        |-- SRv6诊断命令.json
        |-- TAE诊断命令.json
        |-- UCM诊断命令.json
        |-- UNICFG诊断命令.json
        |-- UPLB诊断命令.json
        |-- UP备份诊断命令.json
        |-- VLAN诊断命令.json
        |-- VM管理诊断命令.json
        |-- 信息中心诊断命令.json
        |-- 内存诊断命令.json
        |-- 域名解析诊断命令.json
        |-- 多机备份诊断命令.json
        |-- 接口管理诊断命令.json
        |-- 文件系统管理诊断命令.json
        |-- 进程监控和维护诊断命令.json
        |-- 配置文件管理诊断命令.json
    |-- 37-系统日志信息/
        |-- AAA.json
        |-- ACL.json
        |-- AFT.json
        |-- ANCP.json
        |-- APMGR.json
        |-- APNFWD.json
        |-- ARP.json
        |-- ATK.json
        |-- ATM.json
        |-- BFD.json
        |-- BGP.json
        |-- BIER.json
        |-- BLS.json
        |-- CFD.json
        |-- CFGMAN.json
        |-- CLKM.json
        |-- CONNLMT.json
        |-- CPDR.json
        |-- CUSP.json
        |-- DetNetOAM.json
        |-- DEV.json
        |-- DHCP.json
        |-- DHCPR.json
        |-- DHCPR6.json
        |-- DHCPS.json
        |-- DHCPS6.json
        |-- DHCPSP4.json
        |-- DHCPSP6.json
        |-- DIAG.json
        |-- DLDP.json
        |-- DOMAIN.json
        |-- DOT1X（三层）.json
        |-- DOT1X（二层）.json
        |-- DRNI.json
        |-- EDEV.json
        |-- EIGRP.json
        |-- EM.json
        |-- ERPS.json
        |-- ETH.json
        |-- ETHDRNI.json
        |-- ETHOAM.json
        |-- EVB.json
        |-- EVIISIS.json
        |-- FCLINK.json
        |-- FCOE.json
        |-- FCZONE.json
        |-- FIB.json
        |-- FILTER.json
        |-- FIPSNG.json
        |-- FLOWMON.json
        |-- FLOWSPEC.json
        |-- FTP.json
        |-- gRPC.json
        |-- HA.json
        |-- HQOS.json
        |-- HTTPD.json
        |-- iFIT.json
        |-- IFMON.json
        |-- IFNET.json
        |-- IGMP.json
        |-- IKE.json
        |-- iNQA.json
        |-- INTRACE.json
        |-- IP6ADDR.json
        |-- IP6FW.json
        |-- IPADDR.json
        |-- IPFW.json
        |-- IPOE.json
        |-- IPSEC.json
        |-- IPSG.json
        |-- IRDP.json
        |-- IRF（星堆）.json
        |-- ISIS.json
        |-- ISSU.json
        |-- KHTTP.json
        |-- L2PT.json
        |-- L2TPV2.json
        |-- L2VPN.json
        |-- L3VPN.json
        |-- LAGG.json
        |-- LB.json
        |-- LDP.json
        |-- LIC.json
        |-- LIPC.json
        |-- LLDP.json
        |-- LOAD.json
        |-- LOCAL.json
        |-- LOGIN.json
        |-- LPDT.json
        |-- LS.json
        |-- LSM.json
        |-- LSPV.json
        |-- MAC.json
        |-- MACA.json
        |-- MACSEC.json
        |-- MBFD.json
        |-- MBUF.json
        |-- MDC.json
        |-- MFIB.json
        |-- MGROUP.json
        |-- MLD.json
        |-- MPLS.json
        |-- MSC.json
        |-- MSDP.json
        |-- MTLK.json
        |-- MTP.json
        |-- NA4.json
        |-- NAT.json
        |-- NCM.json
        |-- ND.json
        |-- NETCONF.json
        |-- NETSLICE.json
        |-- NQA.json
        |-- NTP.json
        |-- OAM.json
        |-- OBJP.json
        |-- OFP.json
        |-- OPENSRC(DB-VM).json
        |-- OPENSRC(RSYNC).json
        |-- OPTMOD.json
        |-- OSPF.json
        |-- OSPFV3.json
        |-- PBB.json
        |-- PBR.json
        |-- PCE.json
        |-- PEX.json
        |-- PFILTER.json
        |-- PIM.json
        |-- PING.json
        |-- PKG.json
        |-- PKI.json
        |-- PKT2CPU.json
        |-- PKTCPT.json
        |-- PORTAL.json
        |-- PORTSEC.json
        |-- PPP.json
        |-- PS.json
        |-- PTP.json
        |-- PWDCTL.json
        |-- QOS.json
        |-- RADIUS.json
        |-- RDDC.json
        |-- RESMON.json
        |-- RIP.json
        |-- RIPNG.json
        |-- RM.json
        |-- RMDB.json
        |-- RPR.json
        |-- RRPP.json
        |-- RSVP.json
        |-- RTM.json
        |-- SAVA.json
        |-- SCMD.json
        |-- SCRLSP.json
        |-- SESSION.json
        |-- SFLOW.json
        |-- SHELL.json
        |-- SLSP.json
        |-- SMA.json
        |-- SMLK.json
        |-- SNMP.json
        |-- SRP.json
        |-- SRPM.json
        |-- SRPV6.json
        |-- SRV6.json
        |-- SSHC.json
        |-- SSHS.json
        |-- STAMGR.json
        |-- STM.json
        |-- STP.json
        |-- STRUNK.json
        |-- SYSEVENT.json
        |-- SYSLOG.json
        |-- TACACS.json
        |-- TAE.json
        |-- TBDL.json
        |-- TE.json
        |-- TELNETD.json
        |-- TRILL.json
        |-- UCM.json
        |-- UNICFG.json
        |-- UPBAK.json
        |-- UPLB.json
        |-- UPMGR.json
        |-- URPF.json
        |-- VLAN.json
        |-- VMMGR.json
        |-- VMPATHMTU.json
        |-- VRRP.json
        |-- VSRP.json
        |-- VXLAN.json
        |-- WEB.json
        |-- WIPS.json
        |-- 简介.json
```

## json的背景信息
### json内容切片
```
{
    "example_leafnode": {
        "content": "对于Debug手册:\n\t内容包含命令, 缺省情况, 视图, 缺省用户角色等;\n对于Cli手册:\n\t内容包含命令, 缺省情况, 视图, 缺省用户角色等;\n对于配置手册:\n\t内容包含功能简介, 配置步骤等;",
        "title_1": "标题1名称",
        "title_2": "标题2名称",
        "fullpath": "该叶节点所属文档的全路径"
    },
    "转发与控制分离系统概述/转发与控制分离系统概述命令/display vbras-cp stable state（CP设备）": {
        "content": "**display vbras-cp stable\nstate**命令用来显示转发与控制分离系统的运行状态信息。\n【命令】\n**display vbras-cp stable state** \\[ *service-name* \\]\n【视图】\n任意视图\n【缺省用户角色】\nnetwork-admin\nnetwork-operator\n【参数】\n*service-name*：显示转发与控制分离系统中指定业务模块的稳态和非稳态信息。*service-name*表示转发与控制分离系统中业务模块的名称，取值为：\n-   **cusp**：显示CUSP（Control-/User-plane Separation\n    Protocol，控制与转发分离协议）模块的稳态和非稳态信息。\n-   **db-vm**：显示DB-VM（Database Virtualized\n    Machine）的稳态和非稳态信息。\n-   **health**：显示CPU、内存和磁盘资源模块的稳态和非稳态信息。\n-   **ncm**：显示NCM（NETCONF channel\n    management）模块的稳态和非稳态信息。\n-   **rmdb**：显示RMDB（Remote\n    Database,远程数据库）模块的稳态和非稳态信息。\n-   **up-backup**：显示UP-backup（User plane\n    backup）模块的稳态和非稳态信息。\n-   **uplb**：显示UPLB（User plane load\n    balancer）模块的稳态和非稳态信息。\n-   **vm-group**：显示转发与控制分离系统中所有VM组的稳态和非稳态信息。\n-   **vnfm**：显示VNFM（Virtualized Network Function\n    Managers）模块的稳态和非稳态信息。\n【使用指导】\n...省略N个字符",
        "title_1": "转发与控制分离系统概述",
        "title_2": "转发与控制分离系统概述命令",
        "fullpath": "D:\\Downloads\\pandoc-3.6.3\\B75D104_MD\\00-转发与控制分离业务\\01-转发与控制分离系统概述\\转发与控制分离系统概述命令.md"
    },
	...省略,N个元素
}
```
### json文件构建原则
1. 每个json文件对应原来的docx手册,docx手册由一级标题、二级标题、三级标题、三级标题内容组成;
2. title_1=一级标题,title_2=二级标题,每个元素的key=一级标题/二级标题/三级标题,content=三级标题内容组成;

## postgreSQL数据库的背景信息
### postgreSQL数据库,内容如下
```
postgres=# \l
                                  List of databases
   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
-----------+----------+----------+-------------+-------------+-----------------------
 b75d104   | postgres | UTF8     | zh_CN.UTF-8 | zh_CN.UTF-8 |
 postgres  | postgres | UTF8     | zh_CN.UTF-8 | zh_CN.UTF-8 |
 template0 | postgres | UTF8     | zh_CN.UTF-8 | zh_CN.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
 template1 | postgres | UTF8     | zh_CN.UTF-8 | zh_CN.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
(4 rows)

b75d104-# \dt
           List of relations
 Schema |   Name    | Type  |  Owner
--------+-----------+-------+----------
 public | tree_data | table | postgres
(1 row)

b75d104-# \d tree_data
                              Table "public.tree_data"
  Column   |  Type   | Collation | Nullable |                Default
-----------+---------+-----------+----------+---------------------------------------
 id        | integer |           | not null | nextval('tree_data_id_seq'::regclass)
 parent_id | integer |           |          |
 name      | text    |           | not null |
 content   | text    |           |          |
Indexes:
    "tree_data_pkey" PRIMARY KEY, btree (id)
Foreign-key constraints:
    "tree_data_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES tree_data(id) ON DELETE CASCADE
Referenced by:
    TABLE "tree_data" CONSTRAINT "tree_data_parent_id_fkey" FOREIGN KEY (parent_id) REFERENCES tree_data(id) ON DELETE CASCADE
```
### tree_data表,字段解释
1. parent_id,是某条数据的父节点,
  - 比如某条数据属于某个json,则某个json是某条数据的父节点
  - 比如在文件树中,某个json属于某个文件夹,则某个文件夹是某个json的父节点
2. name,就是每个元素的key=一级标题/二级标题/三级标题,
3. content,就是content=三级标题内容组成
