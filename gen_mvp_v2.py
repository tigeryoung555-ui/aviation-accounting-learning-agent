#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成民航会计学习智能体MVP v2 - 全功能版"""
import json

# 读取题库（脚本同目录，兼容任意部署路径）
import os
_BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_BASE, 'questions.json'), 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 知识库（用于AI答疑RAG检索）
KNOWLEDGE_BASE = [
{"id":"kb1","chapter":"第1章","title":"民航企业经营特点","keywords":"民航 经营 特点 资本密集 技术密集 位移 服务 行业","content":"民用航空运输企业不生产有形物质产品，其产品是旅客和货物的空间位移服务。行业特征：资本密集（单架飞机数亿元）、技术密集（飞行/维修/运控高技术要求）、高固定成本低边际成本、受油价汇率影响大、国际化程度高、季节性周期性明显。"},
{"id":"kb2","chapter":"第1章","title":"民航会计核算特点","keywords":"会计 核算 特点 成本对象 飞行小时 吨公里 航线 机型","content":"民航会计核算特点：1.不生产物质产品，提供位移服务；2.成本计算对象为航线、机型或航班；3.成本计算单位为飞行小时、吨公里、客公里；4.存货核算特殊（航材消耗件、高价周转件、机上供应品）；5.票证结算特殊（国内/国际票证结算）；6.固定资产以飞机为主，折旧方法特殊。"},
{"id":"kb3","chapter":"第1章","title":"民航特殊会计科目","keywords":"科目 航材消耗件 高价周转件 机上供应品 国内票证结算 国际票证结算","content":"民航特有会计科目：存货类-航材消耗件、高价周转件、机上供应品；往来类-国内票证结算、国际票证结算。法规依据：《企业会计准则》《运输（民用航空）企业会计制度》《民航企业会计核算办法》财会[2003]12号。"},
{"id":"kb4","chapter":"第2章","title":"航材消耗件核算","keywords":"航材 消耗件 领用 摊销 计划成本 成本差异 维修","content":"航材消耗件是使用期限较短、单位价值较低、在使用中消耗或不可修复的航空器材（螺栓、密封圈、刹车片等）。可采用实际成本法或计划成本法核算。领用时计入运输成本（维修成本），可采用一次摊销法或分次摊销法。计划成本法下需分摊材料成本差异。"},
{"id":"kb5","chapter":"第2章","title":"高价周转件核算","keywords":"高价周转件 发动机 起落架 APU 飞行小时 摊销","content":"高价周转件是价值高、使用期限长、可多次周转使用的大型飞机部件（发动机、起落架、APU等）。按飞行小时摊销：单位摊销额=(原值-预计净残值)÷预计总飞行小时，本月摊销额=本月实际飞行小时×单位摊销额。摊销额计入运输成本。"},
{"id":"kb6","chapter":"第2章","title":"机上供应品核算","keywords":"机上供应品 餐食 饮料 毛毯 耳机 领用 退回","content":"机上供应品包括为旅客提供的餐食、饮料、报纸杂志、毛毯、耳机等。领用时计入运输成本（机上供应品项目），航班结束后未使用的可退回仓库冲减成本。"},
{"id":"kb7","chapter":"第3章","title":"飞机初始计量","keywords":"飞机 初始计量 入账价值 外购 融资租赁 增值税","content":"外购飞机入账价值=买价+进口关税+运输安装费等达到预定可使用状态前的全部支出。增值税一般纳税人购入飞机的进项税额可抵扣，不计入成本。融资租入飞机按租赁开始日公允价值与最低租赁付款额现值孰低计量。"},
{"id":"kb8","chapter":"第3章","title":"飞机折旧-年限平均法","keywords":"飞机 折旧 年限平均法 机身 折旧年限 净残值 月折旧","content":"飞机机身采用年限平均法计提折旧，折旧年限通常15-20年，净残值率通常5%。计算公式：年折旧额=原值×(1-净残值率)÷预计使用年限；月折旧额=年折旧额÷12。机身损耗与时间相关（老化、锈蚀），适合年限平均法。"},
{"id":"kb9","chapter":"第3章","title":"飞机折旧-工作量法","keywords":"发动机 工作量法 飞行小时 折旧 替换件 单位折旧","content":"发动机替换件采用工作量法（按飞行小时）计提折旧。单位飞行小时折旧额=(原值-预计净残值)÷预计总飞行小时；本月折旧额=本月实际飞行小时×单位飞行小时折旧额。发动机损耗与使用强度直接相关，按飞行小时计提更准确。"},
{"id":"kb10","chapter":"第3章","title":"飞机后续支出","keywords":"A检 B检 C检 D检 资本化 费用化 大修理 后续支出","content":"飞机维修检查分类：A检（最低级别例行检查，费用化）、B检（中等检查，费用化）、C检（高级别检修，符合条件资本化）、D检（最高级别，每6-10年，需拆解机身，通常资本化）。判断原则：符合固定资产确认条件（延长使用寿命、提高性能）的资本化，否则费用化。"},
{"id":"kb11","chapter":"第3章","title":"飞机处置与报废","keywords":"飞机 处置 出售 报废 固定资产清理 资产处置损益 营业外支出","content":"飞机处置通过「固定资产清理」科目核算。出售净损益计入「资产处置损益」（影响营业利润）；报废净损失计入「营业外支出」。会计流程：转入清理→支付清理费用→取得价款→结转净损益。"},
{"id":"kb12","chapter":"第4章","title":"新租赁准则与使用权资产","keywords":"租赁 准则 CAS21 使用权资产 租赁负债 经营租赁 融资租赁 短期租赁","content":"新租赁准则（CAS 21）下，承租人不再区分经营租赁和融资租赁，除短期租赁（≤12个月）和低价值资产租赁外，均确认使用权资产和租赁负债。使用权资产成本=租赁负债初始金额+预付租金+初始直接费用+预计复原成本-租赁激励。"},
{"id":"kb13","chapter":"第4章","title":"租赁负债计量","keywords":"租赁负债 现值 实际利率法 利息费用 摊销 折现率","content":"租赁负债初始计量=租赁付款额的现值（折现率：租赁内含利率，无法确定时用增量借款利率）。后续采用实际利率法计算利息费用（计入财务费用）并调整摊余成本。租赁付款额包括固定付款额、基于指数的可变付款额、购买选择权行权价格、担保余值等。"},
{"id":"kb14","chapter":"第4章","title":"售后回租","keywords":"售后回租 销售成立 使用权资产 租赁负债 处置损益","content":"售后回租：销售成立时，卖方兼承租人终止确认原资产，按原账面价值中与保留使用权相关部分确认使用权资产，差额计入当期损益，同时确认租赁负债。销售不成立时，不终止确认资产，收到款项作为金融负债。售价与公允价值不等时需调整。"},
{"id":"kb15","chapter":"第5章","title":"航油成本核算","keywords":"航油 成本 最大 单项 20% 30% 加权平均 归集","content":"航油成本是航空公司最大的单项运营成本，占运营成本20%-30%。按实际加油量和实际油价归集，可采用加权平均法核算。航油成本包括燃油采购费用、加油服务费、运输储存费。航油套期保值可锁定成本。"},
{"id":"kb16","chapter":"第5章","title":"起降费与航路费","keywords":"起降费 最大起飞重量 MTOW 航路费 民航基础设施建设基金","content":"起降费按飞机最大起飞重量（MTOW）分档计费，重量越大费用越高。航路费（民航基础设施建设基金）按飞行里程征收。均属于直接营运费，计入运输成本。"},
{"id":"kb17","chapter":"第5章","title":"间接营运费分配","keywords":"间接营运费 分配 飞行小时 地面保障 运行指挥 培训","content":"间接营运费是为组织和管理运输生产发生的、不能直接归属某一航班的费用（地面保障、运行指挥、培训、安全管理等）。通常按飞行小时比例分配：分配率=间接营运费总额÷总飞行小时，某机型分配额=该机型飞行小时×分配率。"},
{"id":"kb18","chapter":"第5章","title":"航线成本计算","keywords":"航线成本 单位飞行小时成本 单位客公里成本 毛利率 直接营运费 间接营运费","content":"航线运输总成本=直接营运费+分配的间接营运费。单位飞行小时成本=运输总成本÷飞行小时数。单位客公里成本=客运成本÷旅客周转量（客公里）。航线毛利率=(航线收入-航线成本)÷航线收入×100%。"},
{"id":"kb19","chapter":"第6章","title":"国内票证结算与BSP","keywords":"国内票证结算 BSP 账单结算计划 客票 结算","content":"国内票证结算是民航特有科目，核算国内航线票证结算款项。BSP（Billing and Settlement Plan，账单结算计划）是IATA推行的中性票证结算系统，实现票款集中清算，减少航空公司间资金占用。"},
{"id":"kb20","chapter":"第6章","title":"国际票证结算与比例分摊","keywords":"国际票证结算 联运 比例分摊 IATA 多家承运人","content":"国际联运涉及多家航空公司共同完成运输，收入按IATA比例分摊手册（Prorate Manual）规定的比例在各承运人之间分配。使用「国际票证结算」科目核算，涉及外币结算。"},
{"id":"kb21","chapter":"第6章","title":"运输收入确认与合同负债","keywords":"收入确认 运输服务 合同负债 空中交通负债 售票 航班到达","content":"客运收入在运输服务提供时（航班到达）确认。售票时未运输的票款确认为合同负债（空中交通负债），是航空公司最大的流动负债项目之一。旅客误机且不可退票时，履约义务解除，转为收入。"},
{"id":"kb22","chapter":"第6章","title":"常旅客里程计划","keywords":"常旅客 里程 奖励 合同负债 收入分摊 单独售价 兑换","content":"常旅客奖励里程构成单项履约义务。票款按运输服务和奖励里程的单独售价比例分摊：运输服务分摊比例=运输服务单独售价÷(运输服务+奖励里程)单独售价。奖励里程部分确认为合同负债，兑换时转为运输收入，到期未兑换也转为收入。"},
{"id":"kb23","chapter":"第7章","title":"应付债券与可转换债券","keywords":"应付债券 实际利率法 折价 溢价 可转换债券 分拆 负债成分 权益成分","content":"应付债券折价或溢价采用实际利率法摊销。可转换公司债券初始确认时应分拆：负债成分=未来现金流量现值（不含转股权）→应付债券；权益成分=发行价格-负债成分→其他权益工具。转股时按账面价值结转，不确认损益。"},
{"id":"kb24","chapter":"第8章","title":"现金流量表","keywords":"现金流量表 经营活动 投资活动 筹资活动 飞机购置 票款 租赁本金","content":"经营活动：票款收入（流入）、航油/薪酬/起降费（流出）。投资活动：飞机购置（大额流出）、飞机处置（流入）。筹资活动：借款/发债（流入）、租赁本金偿还（流出）、股利（流出）。租赁本金偿还是筹资活动，利息可计入经营或筹资活动。"},
{"id":"kb25","chapter":"第9章","title":"民航财务分析指标","keywords":"客座率 载运率 飞机日利用率 资产负债率 利息保障倍数 航线毛利率 单位飞行小时利润","content":"民航特色运营指标：客座率=实际旅客周转量÷可提供客公里；载运率=实际总周转量÷可提供总周转量；飞机日利用率=日均飞行小时。财务指标：资产负债率（航司普遍70%左右）、利息保障倍数、航线毛利率、单位飞行小时利润、单位客公里利润。"},
{"id":"kb26","chapter":"第9章","title":"航油价格敏感性分析","keywords":"航油 敏感性 油价 利润 影响 套期保值","content":"航油价格敏感性分析测算油价变动±10%、±20%对利润的影响。航油成本占运营成本25%时，油价上涨20%可能导致利润下降50%。航空公司可通过航油套期保值、征收燃油附加费、优化机队等方式管理油价风险。"},
{"id":"kb27","chapter":"第10章","title":"外币交易核算","keywords":"外币 交易 即期汇率 期末调整 货币性项目 汇兑差额 财务费用","content":"外币交易初始确认采用交易发生日即期汇率。期末外币货币性项目按期末即期汇率调整，汇兑差额计入财务费用。以历史成本计量的外币非货币性项目期末不调整。"},
{"id":"kb28","chapter":"第10章","title":"外币报表折算与合并","keywords":"外币报表折算 期末汇率 其他综合收益 合并范围 控制","content":"境外经营财务报表折算：资产负债按期末即期汇率，收入费用按交易发生日汇率（或平均汇率），折算差额计入其他综合收益。合并财务报表以「控制」为基础确定合并范围。民航集团合并特点：跨境子公司多、关联交易复杂（代码共享、内部租赁）。"},
]

# 知识点内容（用于知识学习模块）
CHAPTER_CONTENT = {
"第1章 概论": {"hours":"4学时","kp":["民航企业经营特点","民航会计核算特点","民航特殊会计科目"],"content":"""
<h4>一、民航运输企业经营特点</h4>
<p>民用航空运输企业是指使用民用航空器运送旅客、行李、邮件或货物的企业法人。核心业务是提供空中位移服务，不生产有形物质产品。</p>
<div class="highlight">行业特征：资本密集（单架飞机数亿元）、技术密集、高固定成本低边际成本、受油价汇率影响大、国际化程度高。</div>
<h4>二、民航会计核算特点</h4>
<p>1.不生产物质产品，提供位移服务；2.成本计算对象为航线/机型/航班；3.成本计算单位为飞行小时/吨公里/客公里；4.存货核算特殊；5.票证结算特殊；6.飞机折旧方法特殊。</p>
<h4>三、民航特殊会计科目</h4>
<div class="formula">存货类：航材消耗件、高价周转件、机上供应品\n往来类：国内票证结算、国际票证结算</div>
<h4>四、法规依据</h4>
<p>《企业会计准则》《运输（民用航空）企业会计制度》《民航企业会计核算办法》（财会[2003]12号）。</p>"""},
"第2章 流动资产": {"hours":"6学时","kp":["航材消耗件核算","高价周转件核算","机上供应品核算"],"content":"""
<h4>一、航材消耗件</h4>
<p>使用期限较短、单位价值较低、在使用中消耗或不可修复的航空器材。领用时计入运输成本（维修成本），可采用一次或分次摊销法。计划成本法下需分摊材料成本差异。</p>
<h4>二、高价周转件</h4>
<p>价值高、使用期限长、可多次周转使用的大型飞机部件（发动机、起落架、APU等）。按飞行小时摊销。</p>
<div class="formula">单位摊销额=(原值-预计净残值)÷预计总飞行小时\n本月摊销额=本月实际飞行小时×单位摊销额</div>
<h4>三、机上供应品</h4>
<p>餐食、饮料、报纸杂志、毛毯、耳机等。领用时计入运输成本，未使用可退回冲减。</p>"""},
"第3章 飞机发动机": {"hours":"8学时","kp":["飞机初始计量","飞机折旧-年限平均法","飞机折旧-工作量法","飞机后续支出","飞机处置与报废"],"content":"""
<h4>一、飞机初始计量</h4>
<p>外购飞机入账价值=买价+关税+运输安装费等（进项税可抵扣）。融资租入按公允价值与最低租赁付款额现值孰低计量。</p>
<h4>二、飞机折旧（核心）</h4>
<div class="highlight">机身：年限平均法，15-20年，净残值率5%。\n发动机替换件：工作量法，按飞行小时计提。</div>
<div class="formula">年限平均法：年折旧额=原值×(1-净残值率)÷使用年限\n工作量法：单位折旧额=(原值-净残值)÷预计总飞行小时</div>
<h4>三、后续支出</h4>
<p>A检/B检费用化；C检/D检符合条件资本化。</p>
<h4>四、处置</h4>
<p>通过「固定资产清理」核算，出售净损益→资产处置损益，报废净损失→营业外支出。</p>"""},
"第4章 飞机租赁": {"hours":"6学时","kp":["租赁分类","使用权资产确认","租赁负债计量","售后回租"],"content":"""
<h4>一、新租赁准则核心变化</h4>
<div class="highlight">承租人不再区分经营/融资租赁，除短期租赁（≤12月）和低价值租赁外，均确认使用权资产和租赁负债。</div>
<h4>二、使用权资产</h4>
<div class="formula">成本=租赁负债初始金额+预付租金+初始直接费用+预计复原成本-租赁激励</div>
<h4>三、租赁负债</h4>
<p>初始=租赁付款额现值；后续=实际利率法摊销（利息计入财务费用）。</p>
<h4>四、售后回租</h4>
<p>销售成立：终止确认原资产+确认使用权资产和租赁负债；销售不成立：作为金融负债。</p>"""},
"第5章 运输成本": {"hours":"8学时","kp":["成本核算对象","航油成本核算","起降费与航路费","机组薪酬核算","间接营运费分配","航线成本计算"],"content":"""
<h4>一、成本核算体系</h4>
<p>核算对象：航线/机型/航班。计算单位：飞行小时/吨公里/客公里。成本项目：直接营运费+间接营运费。</p>
<h4>二、直接营运费</h4>
<div class="highlight">航油成本（最大，占20-30%）、起降费（按最大起飞重量）、机组薪酬（基本工资+飞行小时费）、飞机折旧及租赁、维修、机上供应品、航路费。</div>
<h4>三、间接营运费分配</h4>
<div class="formula">分配率=间接营运费总额÷总飞行小时\n某机型分配额=该机型飞行小时×分配率</div>
<h4>四、航线成本</h4>
<div class="formula">单位飞行小时成本=运输总成本÷飞行小时数\n单位客公里成本=客运成本÷旅客周转量</div>"""},
"第6章 票证收入": {"hours":"6学时","kp":["国内票证结算","国际票证结算","运输收入确认","常旅客里程计划"],"content":"""
<h4>一、票证结算</h4>
<p>国内票证结算（BSP账单结算计划）、国际票证结算（联运比例分摊）。</p>
<h4>二、收入确认</h4>
<div class="highlight">运输服务提供时（航班到达）确认收入。售票未运输票款→合同负债（空中交通负债）。</div>
<h4>三、常旅客里程计划（重点）</h4>
<div class="formula">票款分摊：\n运输服务比例=运输服务单独售价÷(运输服务+奖励里程)单独售价\n奖励里程部分→合同负债，兑换时→主营业务收入</div>"""},
"第7章 负债权益": {"hours":"4学时","kp":["流动负债","非流动负债","所有者权益"],"content":"""
<h4>一、流动负债</h4>
<p>短期借款、应付账款、应付职工薪酬、合同负债（民航特色大额项目）。</p>
<h4>二、非流动负债</h4>
<p>长期借款、应付债券（实际利率法）、可转换公司债券（分拆为负债+权益成分）、租赁负债。</p>
<h4>三、所有者权益</h4>
<p>实收资本（股本）、资本公积、其他综合收益、盈余公积、未分配利润。</p>"""},
"第8章 财务报告": {"hours":"4学时","kp":["资产负债表编制","利润表编制","现金流量表编制","分部报告"],"content":"""
<h4>一、资产负债表特殊列报</h4>
<p>高价周转件→存货；合同负债→流动负债；使用权资产→非流动资产；租赁负债→分流动/非流动。</p>
<h4>二、现金流量表</h4>
<div class="highlight">经营：票款流入、航油/薪酬流出；投资：飞机购置流出；筹资：借款流入、租赁本金流出。</div>
<h4>三、分部报告</h4>
<p>可按航线、地区、客运/货运维度编制。</p>"""},
"第9章 报表分析": {"hours":"4学时","kp":["偿债能力分析","营运能力分析","盈利能力分析","航油敏感性分析"],"content":"""
<h4>一、偿债能力</h4>
<div class="formula">资产负债率=负债总额÷资产总额\n利息保障倍数=息税前利润÷利息费用</div>
<p>航司资产负债率普遍70%左右。</p>
<h4>二、营运能力（民航特色）</h4>
<div class="formula">客座率=实际旅客周转量÷可提供客公里\n载运率=实际总周转量÷可提供总周转量</div>
<h4>三、盈利能力</h4>
<p>航线毛利率、单位飞行小时利润、单位客公里利润。</p>
<h4>四、航油敏感性分析</h4>
<p>测算油价变动对利润影响，航油占比25%时油价+20%可能导致利润-50%。</p>"""},
"第10章 外币合并": {"hours":"2学时","kp":["外币交易核算","外币报表折算","合并报表基础"],"content":"""
<h4>一、外币交易</h4>
<p>初始确认用交易日即期汇率；期末货币性项目按期末汇率调整，汇兑差额计入财务费用。</p>
<h4>二、外币报表折算</h4>
<p>资产负债用期末汇率，收入费用用发生日汇率，差额计入其他综合收益。</p>
<h4>三、合并报表</h4>
<p>以「控制」为基础。民航集团特点：跨境子公司多、关联交易复杂、常旅客跨子公司。</p>"""},
}

# 主观题关键词评分规则
def get_keywords(q):
    """根据题目解析提取评分关键词"""
    explain = q.get('explain','') or ''
    qtype = q.get('type','')
    # 从解析中提取关键会计科目和数字
    import re
    keywords = []
    # 提取会计科目（借/贷后面的科目）
    subjects = re.findall(r'[借贷]：?\s*([^\n（(]+?)(?:\s|$|\n)', explain)
    for s in subjects:
        s = s.strip()
        if 2 <= len(s) <= 20 and not any(c in s for c in '0123456789.万元亿'):
            keywords.append(s)
    # 提取关键数字
    numbers = re.findall(r'(\d+\.?\d*)\s*(万元|亿元|元|%|小时)', explain)
    for n, u in numbers[:5]:
        keywords.append(f"{n}{u}")
    # 提取关键术语
    terms = ['合同负债','使用权资产','租赁负债','累计折旧','固定资产清理','资产处置损益',
             '国内票证结算','国际票证结算','航材消耗件','高价周转件','主营业务成本','主营业务收入',
             '财务费用','管理费用','银行存款','应付债券','其他权益工具','其他综合收益',
             '年限平均法','工作量法','实际利率法','飞行小时','客座率','载运率',
             '资本化','费用化','现值','摊销','折旧','汇兑差额']
    for t in terms:
        if t in explain and t not in keywords:
            keywords.append(t)
    return list(set(keywords))[:15]

# 为每道题添加关键词
for q in questions:
    if q['type'] in ['分录题','计算分析题','简答题','名词解释','案例题']:
        q['keywords'] = get_keywords(q)
    else:
        q['keywords'] = []

# 构建HTML
html_template = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>民航运输企业会计学习智能体 v2.0</title>
<link rel="stylesheet" href="https://miaoda.feishu.cn/fonts/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap">
<style>
:root{--primary:#1a56a4;--primary-light:#e8f0fb;--primary-dark:#0f3d7a;--accent:#00a0b0;--success:#22a06b;--warning:#e8a317;--danger:#d94040;--bg:#f4f6fa;--card:#fff;--text:#1e293b;--text-light:#64748b;--border:#e2e8f0;--shadow:0 2px 12px rgba(26,86,164,0.08);}
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Noto Sans SC',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.6;}
.app{display:flex;min-height:100vh;}
.sidebar{width:240px;background:linear-gradient(180deg,var(--primary-dark),var(--primary));color:#fff;padding:20px 0;position:fixed;height:100vh;overflow-y:auto;z-index:100;}
.sidebar .logo{padding:0 20px 20px;border-bottom:1px solid rgba(255,255,255,0.15);}
.sidebar .logo h1{font-size:17px;font-weight:700;line-height:1.4;}
.sidebar .logo p{font-size:11px;opacity:0.7;margin-top:4px;}
.sidebar .role-tabs{display:flex;padding:12px 16px;gap:6px;}
.sidebar .role-tab{flex:1;padding:6px 0;text-align:center;font-size:12px;border-radius:6px;cursor:pointer;background:rgba(255,255,255,0.1);transition:all 0.2s;}
.sidebar .role-tab.active{background:var(--accent);font-weight:600;}
.nav{padding:8px 0;}
.nav-section{font-size:11px;text-transform:uppercase;opacity:0.5;padding:12px 24px 6px;letter-spacing:1px;}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 24px;cursor:pointer;transition:all 0.2s;font-size:13px;color:rgba(255,255,255,0.8);border-left:3px solid transparent;}
.nav-item:hover{background:rgba(255,255,255,0.1);color:#fff;}
.nav-item.active{background:rgba(255,255,255,0.15);color:#fff;border-left-color:var(--accent);font-weight:500;}
.nav-item svg{width:18px;height:18px;flex-shrink:0;}
.nav-badge{margin-left:auto;background:var(--accent);color:#fff;font-size:10px;padding:1px 7px;border-radius:9px;font-weight:600;}
.main{margin-left:240px;flex:1;padding:28px;max-width:1280px;}
.page-header{margin-bottom:20px;}
.page-header h2{font-size:22px;font-weight:700;color:var(--primary-dark);}
.page-header p{color:var(--text-light);font-size:13px;margin-top:3px;}
.card{background:var(--card);border-radius:12px;padding:22px;box-shadow:var(--shadow);margin-bottom:18px;}
.card h3{font-size:15px;font-weight:600;margin-bottom:14px;color:var(--primary-dark);}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
.stat-card{background:var(--card);border-radius:12px;padding:18px;box-shadow:var(--shadow);position:relative;overflow:hidden;}
.stat-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;}
.stat-card.blue::before{background:var(--primary);}.stat-card.teal::before{background:var(--accent);}
.stat-card.green::before{background:var(--success);}.stat-card.orange::before{background:var(--warning);}
.stat-card .label{font-size:12px;color:var(--text-light);margin-bottom:6px;}
.stat-card .value{font-size:26px;font-weight:700;color:var(--primary-dark);}
.stat-card .sub{font-size:11px;color:var(--text-light);margin-top:3px;}
.chapter-list{display:grid;gap:10px;}
.chapter-item{display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--card);border-radius:10px;box-shadow:var(--shadow);cursor:pointer;transition:all 0.2s;border:1px solid transparent;}
.chapter-item:hover{border-color:var(--primary);transform:translateX(3px);}
.chapter-num{width:36px;height:36px;border-radius:8px;background:var(--primary-light);color:var(--primary);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0;}
.chapter-info{flex:1;}.chapter-info .title{font-weight:600;font-size:14px;}
.chapter-info .meta{font-size:11px;color:var(--text-light);margin-top:2px;}
.chapter-progress{width:100px;height:7px;background:var(--border);border-radius:4px;overflow:hidden;}
.chapter-progress .bar{height:100%;background:var(--success);border-radius:4px;transition:width 0.3s;}
.knowledge-content{line-height:1.8;}
.knowledge-content h4{color:var(--primary);font-size:14px;margin:18px 0 8px;padding-left:10px;border-left:3px solid var(--primary);}
.knowledge-content p{margin-bottom:10px;font-size:13px;}
.knowledge-content .highlight{background:var(--primary-light);padding:10px 14px;border-radius:8px;margin:10px 0;font-size:13px;}
.knowledge-content .formula{background:#f8fafc;padding:8px 14px;border-radius:6px;font-family:monospace;font-size:12px;margin:6px 0;border-left:3px solid var(--accent);white-space:pre-line;}
.quiz-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px;}
.quiz-filters{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.filter-btn{padding:6px 14px;border:1px solid var(--border);border-radius:18px;background:#fff;cursor:pointer;font-size:12px;transition:all 0.2s;}
.filter-btn:hover{border-color:var(--primary);}
.filter-btn.active{background:var(--primary);color:#fff;border-color:var(--primary);}
select.filter-btn{appearance:none;padding-right:24px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center;}
.quiz-card{background:var(--card);border-radius:12px;padding:20px;box-shadow:var(--shadow);margin-bottom:14px;}
.quiz-meta{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;align-items:center;}
.tag{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:500;}
.tag.chapter{background:var(--primary-light);color:var(--primary);}
.tag.type{background:#f0fdf4;color:var(--success);}
.tag.diff-easy{background:#fef3c7;color:#92400e;}
.tag.diff-mid{background:#dbeafe;color:#1e40af;}
.tag.diff-hard{background:#fee2e2;color:#991b1b;}
.tag.aviation{background:#ecfeff;color:#155e75;}
.quiz-question{font-size:14px;font-weight:500;margin-bottom:14px;line-height:1.7;}
.quiz-options{display:flex;flex-direction:column;gap:8px;}
.quiz-option{padding:10px 14px;border:1px solid var(--border);border-radius:8px;cursor:pointer;transition:all 0.2s;font-size:13px;display:flex;align-items:center;gap:10px;}
.quiz-option:hover{border-color:var(--primary);background:var(--primary-light);}
.quiz-option.selected{border-color:var(--primary);background:var(--primary-light);font-weight:500;}
.quiz-option.correct{border-color:var(--success);background:#f0fdf4;}
.quiz-option.wrong{border-color:var(--danger);background:#fef2f2;}
.quiz-option .opt-label{width:22px;height:22px;border-radius:50%;background:var(--border);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0;}
.quiz-option.selected .opt-label{background:var(--primary);color:#fff;}
.quiz-option.correct .opt-label{background:var(--success);color:#fff;}
.quiz-option.wrong .opt-label{background:var(--danger);color:#fff;}
.subjective-area{width:100%;min-height:100px;padding:10px;border:1px solid var(--border);border-radius:8px;font-size:13px;font-family:inherit;resize:vertical;line-height:1.6;}
.subjective-area:focus{outline:none;border-color:var(--primary);}
.quiz-actions{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap;}
.btn{padding:8px 20px;border:none;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500;transition:all 0.2s;}
.btn-primary{background:var(--primary);color:#fff;}.btn-primary:hover{background:var(--primary-dark);}
.btn-primary:disabled{background:var(--border);cursor:not-allowed;}
.btn-outline{background:#fff;border:1px solid var(--border);color:var(--text);}
.btn-outline:hover{border-color:var(--primary);color:var(--primary);}
.btn-success{background:var(--success);color:#fff;}
.btn-sm{padding:5px 12px;font-size:12px;}
.quiz-result{margin-top:14px;padding:14px;border-radius:8px;display:none;}
.quiz-result.show{display:block;}
.quiz-result.correct{background:#f0fdf4;border:1px solid #bbf7d0;}
.quiz-result.wrong{background:#fef2f2;border:1px solid #fecaca;}
.quiz-result.partial{background:#fffbeb;border:1px solid #fde68a;}
.quiz-result .result-title{font-weight:600;margin-bottom:6px;font-size:14px;}
.quiz-result .result-explain{font-size:12px;color:var(--text-light);line-height:1.7;margin-top:6px;}
.score-bar{height:8px;background:var(--border);border-radius:4px;overflow:hidden;margin:6px 0;}
.score-bar .fill{height:100%;border-radius:4px;transition:width 0.5s;}
.score-overview{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px;}
.score-card{background:var(--card);border-radius:12px;padding:20px;box-shadow:var(--shadow);text-align:center;}
.score-card .score-num{font-size:32px;font-weight:700;color:var(--primary);}
.score-card .score-label{font-size:12px;color:var(--text-light);margin-top:4px;}
.chapter-score-row{display:flex;align-items:center;gap:14px;padding:10px 0;border-bottom:1px solid var(--border);}
.chapter-score-row .cs-name{width:160px;font-size:13px;flex-shrink:0;}
.chapter-score-row .cs-bar{flex:1;height:8px;background:var(--border);border-radius:4px;overflow:hidden;}
.chapter-score-row .cs-fill{height:100%;border-radius:4px;}
.chapter-score-row .cs-score{width:70px;text-align:right;font-weight:600;font-size:13px;}
.wrong-list{display:flex;flex-direction:column;gap:10px;}
.wrong-item{background:var(--card);border-radius:10px;padding:14px;box-shadow:var(--shadow);border-left:3px solid var(--danger);}
.wrong-item .wq{font-size:13px;margin-bottom:6px;}
.wrong-item .wa{font-size:12px;color:var(--text-light);}
/* AI答疑 */
.ai-chat{display:flex;flex-direction:column;height:600px;}
.ai-messages{flex:1;overflow-y:auto;padding:10px;display:flex;flex-direction:column;gap:12px;}
.ai-msg{max-width:80%;padding:12px 16px;border-radius:12px;font-size:13px;line-height:1.7;}
.ai-msg.user{align-self:flex-end;background:var(--primary);color:#fff;border-bottom-right-radius:4px;}
.ai-msg.bot{align-self:flex-start;background:#f1f5f9;color:var(--text);border-bottom-left-radius:4px;}
.ai-msg.bot .src{font-size:11px;color:var(--text-light);margin-top:8px;padding-top:6px;border-top:1px solid var(--border);}
.ai-input{display:flex;gap:10px;padding:14px;border-top:1px solid var(--border);}
.ai-input input{flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:13px;font-family:inherit;}
.ai-input input:focus{outline:none;border-color:var(--primary);}
.ai-suggestions{display:flex;gap:8px;flex-wrap:wrap;padding:10px 14px;}
.ai-suggestion{padding:5px 12px;background:var(--primary-light);color:var(--primary);border-radius:14px;font-size:12px;cursor:pointer;transition:all 0.2s;}
.ai-suggestion:hover{background:var(--primary);color:#fff;}
.ai-status{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--text-light);margin-left:10px;}
.ai-status::before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--text-light);}
.ai-status.online::before{background:var(--success);}
.ai-status.offline::before{background:var(--warning);}
/* 教师端 */
.teacher-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;}
.t-stat{background:var(--card);border-radius:12px;padding:18px;box-shadow:var(--shadow);}
.t-stat .t-label{font-size:12px;color:var(--text-light);}
.t-stat .t-value{font-size:24px;font-weight:700;color:var(--primary-dark);margin-top:4px;}
.t-stat .t-sub{font-size:11px;color:var(--text-light);margin-top:2px;}
.table-wrap{overflow-x:auto;}
.data-table{width:100%;border-collapse:collapse;font-size:12px;}
.data-table th{background:var(--primary-light);color:var(--primary-dark);padding:10px 8px;text-align:left;font-weight:600;border-bottom:2px solid var(--primary);}
.data-table td{padding:8px;border-bottom:1px solid var(--border);}
.data-table tr:hover{background:var(--primary-light);}
.exam-config{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.config-group label{display:block;font-size:12px;color:var(--text-light);margin-bottom:4px;}
.config-group input,.config-group select{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:6px;font-size:13px;}
.exam-preview{margin-top:16px;}
.exam-q{padding:12px;background:#f8fafc;border-radius:8px;margin-bottom:8px;font-size:13px;}
.exam-q .eq-num{font-weight:600;color:var(--primary);margin-right:8px;}
.class-chart{height:300px;position:relative;}
.bar-chart{display:flex;align-items:flex-end;gap:12px;height:250px;padding:20px 0;border-bottom:2px solid var(--border);}
.bar-item{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;}
.bar{width:100%;max-width:50px;background:linear-gradient(180deg,var(--primary),var(--accent));border-radius:4px 4px 0 0;transition:height 0.5s;position:relative;}
.bar .bar-val{position:absolute;top:-20px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:600;color:var(--primary-dark);}
.bar-label{font-size:11px;color:var(--text-light);text-align:center;}
@media(max-width:768px){.sidebar{width:56px;}.sidebar .logo h1,.sidebar .logo p,.nav-item span,.nav-badge,.nav-section,.role-tab{display:none;}.main{margin-left:56px;padding:14px;}.stats-grid,.teacher-stats{grid-template-columns:repeat(2,1fr);}.score-overview{grid-template-columns:1fr;}.exam-config{grid-template-columns:1fr;}}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.view{animation:fadeIn 0.3s ease;}.hidden{display:none;}
.toast{position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;color:#fff;font-size:13px;z-index:9999;animation:fadeIn 0.3s;}
.toast.success{background:var(--success);}.toast.error{background:var(--danger);}.toast.info{background:var(--primary);}
</style>
</head>
<body>
<div class="app">
<aside class="sidebar">
<div class="logo"><h1>民航运输企业会计</h1><p>学习智能体 v2.0</p></div>
<div class="role-tabs">
<div class="role-tab active" data-role="student">学生端</div>
<div class="role-tab" data-role="teacher">教师端</div>
</div>
<nav class="nav" id="studentNav">
<div class="nav-section">学习中心</div>
<div class="nav-item active" data-view="dashboard"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg><span>学习仪表盘</span></div>
<div class="nav-item" data-view="knowledge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg><span>知识学习</span></div>
<div class="nav-item" data-view="quiz"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg><span>智能练习</span><span class="nav-badge" id="quizBadge">0</span></div>
<div class="nav-item" data-view="ai"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg><span>AI答疑</span></div>
<div class="nav-item" data-view="score"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg><span>成绩分析</span></div>
<div class="nav-item" data-view="wrong"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg><span>错题本</span></div>
</nav>
<nav class="nav hidden" id="teacherNav">
<div class="nav-section">教学管理</div>
<div class="nav-item" data-view="t-dashboard"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg><span>教学概览</span></div>
<div class="nav-item" data-view="t-bank"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg><span>题库管理</span></div>
<div class="nav-item" data-view="t-exam"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg><span>自动组卷</span></div>
<div class="nav-item" data-view="t-class"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg><span>班级成绩</span></div>
</nav>
</aside>
<main class="main">
<!-- 学生端视图 -->
<div id="view-dashboard" class="view">
<div class="page-header"><h2>学习仪表盘</h2><p>掌握你的学习进度，民航运输企业会计智能体为你护航</p></div>
<div class="stats-grid">
<div class="stat-card blue"><div class="label">题库总量</div><div class="value" id="statTotal">0</div><div class="sub">10章39个知识点</div></div>
<div class="stat-card teal"><div class="label">已完成练习</div><div class="value" id="statDone">0</div><div class="sub">累计答题次数</div></div>
<div class="stat-card green"><div class="label">正确率</div><div class="value" id="statRate">0%</div><div class="sub">客观题自动评阅</div></div>
<div class="stat-card orange"><div class="label">错题数</div><div class="value" id="statWrong">0</div><div class="sub">待复习巩固</div></div>
</div>
<div class="card"><h3>课程章节（点击进入学习）</h3><div class="chapter-list" id="chapterList"></div></div>
</div>

<div id="view-knowledge" class="view hidden">
<div class="page-header"><h2>知识学习</h2><p>系统学习民航运输企业会计10章核心知识</p></div>
<div id="knowledgeChapterSelect" style="margin-bottom:16px;"></div>
<div class="card" id="knowledgeContent"></div>
</div>

<div id="view-quiz" class="view hidden">
<div class="page-header"><h2>智能练习</h2><p>206题全量题库 · 客观题自动评阅 · 主观题关键词初评</p></div>
<div class="quiz-header">
<div class="quiz-filters" id="chapterFilter"></div>
<div class="quiz-filters" id="typeFilter"></div>
</div>
<div id="quizList"></div>
</div>

<div id="view-ai" class="view hidden">
<div class="page-header"><h2>AI答疑助手</h2><span class="ai-status" id="aiStatus">检测中…</span><p>基于民航会计知识库的检索增强答疑（RAG），输入问题获取专业解答。可选接入本地LLM后端获得生成式回答。</p></div>
<div class="card" style="padding:0;overflow:hidden;">
<div class="ai-suggestions" id="aiSuggestions"></div>
<div class="ai-messages" id="aiMessages"></div>
<div class="ai-input">
<input type="text" id="aiInput" placeholder="输入你的问题，如：飞机折旧为什么用两种方法？">
<button class="btn btn-primary" onclick="sendAI()">发送</button>
</div>
</div>
</div>

<div id="view-score" class="view hidden">
<div class="page-header"><h2>成绩分析</h2><p>自动生成个人学习成绩和知识点掌握分析</p></div>
<div class="score-overview">
<div class="score-card"><div class="score-num" id="totalAnswered">0</div><div class="score-label">累计答题数</div></div>
<div class="score-card"><div class="score-num" id="totalCorrect">0</div><div class="score-label">答对题数</div></div>
<div class="score-card"><div class="score-num" id="overallRate">0%</div><div class="score-label">综合正确率</div></div>
</div>
<div class="card"><h3>各章正确率</h3><div class="chapter-scores" id="chapterScores"></div></div>
<div class="card"><h3>知识点掌握度（薄弱点优先）</h3><div id="kpMastery"></div></div>
</div>

<div id="view-wrong" class="view hidden">
<div class="page-header"><h2>错题本</h2><p>自动归集错题，针对性复习薄弱知识点</p></div>
<div class="wrong-list" id="wrongList"></div>
</div>

<!-- 教师端视图 -->
<div id="view-t-dashboard" class="view hidden">
<div class="page-header"><h2>教学概览</h2><p>题库、班级、成绩一站式管理</p></div>
<div class="teacher-stats">
<div class="t-stat"><div class="t-label">题库总量</div><div class="t-value" id="tTotal">0</div><div class="t-sub">覆盖10章</div></div>
<div class="t-stat"><div class="t-label">班级人数</div><div class="t-value">45</div><div class="t-sub">模拟班级数据</div></div>
<div class="t-stat"><div class="t-label">平均正确率</div><div class="t-value" id="tAvgRate">0%</div><div class="t-sub">班级整体</div></div>
<div class="t-stat"><div class="t-label">已组试卷</div><div class="t-value" id="tExamCount">0</div><div class="t-sub">历史组卷</div></div>
</div>
<div class="card"><h3>题库分布</h3><div id="bankDistribution"></div></div>
<div class="card"><h3>班级成绩分布</h3><div class="bar-chart" id="classChart"></div></div>
</div>

<div id="view-t-bank" class="view hidden">
<div class="page-header"><h2>题库管理</h2><p>浏览、筛选、统计全部206道题目</p></div>
<div class="quiz-header">
<div class="quiz-filters" id="bankChapterFilter"></div>
<div class="quiz-filters" id="bankTypeFilter"></div>
<div style="font-size:13px;color:var(--text-light);">共 <span id="bankCount">0</span> 题</div>
</div>
<div class="card" style="padding:0;"><div class="table-wrap"><table class="data-table" id="bankTable"><thead><tr><th>编号</th><th>章节</th><th>题型</th><th>难度</th><th>题干</th><th>分值</th><th>民航特色</th></tr></thead><tbody></tbody></table></div></div>
</div>

<div id="view-t-exam" class="view hidden">
<div class="page-header"><h2>自动组卷</h2><p>按题型、难度、知识点约束自动生成试卷</p></div>
<div class="card">
<h3>组卷参数</h3>
<div class="exam-config">
<div class="config-group"><label>试卷名称</label><input type="text" id="examName" value="民航会计期中模拟试卷"></div>
<div class="config-group"><label>考试时长（分钟）</label><input type="number" id="examDuration" value="90"></div>
<div class="config-group"><label>章节范围</label><select id="examChapter"><option value="全部">全部章节</option>__CHAPTER_OPTIONS__</select></div>
<div class="config-group"><label>难度分布</label><select id="examDiff"><option value="balanced">均衡（易3:中5:难2）</option><option value="easy">偏易（易5:中4:难1）</option><option value="hard">偏难（易1:中4:难5）</option></select></div>
<div class="config-group"><label>单选题数量</label><input type="number" id="nSingle" value="15" min="0"></div>
<div class="config-group"><label>多选题数量</label><input type="number" id="nMulti" value="5" min="0"></div>
<div class="config-group"><label>判断题数量</label><input type="number" id="nJudge" value="10" min="0"></div>
<div class="config-group"><label>主观题数量</label><input type="number" id="nSubj" value="3" min="0"></div>
</div>
<div style="margin-top:16px;"><button class="btn btn-primary" onclick="generateExam()">生成试卷</button>
<button class="btn btn-outline" onclick="exportExam()">导出试卷</button></div>
</div>
<div class="card hidden" id="examResult"><h3>试卷预览</h3><div id="examPreview"></div></div>
</div>

<div id="view-t-class" class="view hidden">
<div class="page-header"><h2>班级成绩分析</h2><p>模拟班级数据 · 学生成绩排名 · 知识点掌握热力图</p></div>
<div class="score-overview">
<div class="score-card"><div class="score-num">78.5</div><div class="score-label">班级平均分</div></div>
<div class="score-card"><div class="score-num">85%</div><div class="score-label">及格率</div></div>
<div class="score-card"><div class="score-num">12.3</div><div class="score-label">标准差</div></div>
</div>
<div class="card"><h3>成绩分布直方图</h3><div class="bar-chart" id="scoreDistChart"></div></div>
<div class="card"><h3>学生成绩排名</h3><div class="table-wrap"><table class="data-table" id="classRankTable"><thead><tr><th>排名</th><th>学号</th><th>姓名</th><th>平时成绩</th><th>期中成绩</th><th>期末成绩</th><th>总评</th><th>等级</th></tr></thead><tbody></tbody></table></div></div>
<div class="card"><h3>各章班级正确率（知识点掌握热力图）</h3><div id="classChapterRate"></div></div>
</div>
</main>
</div>
<div id="toastContainer"></div>

<script>
// ===== 数据 =====
const QUESTIONS = __QUESTIONS_JSON__;
const KNOWLEDGE_BASE = __KB_JSON__;
const CHAPTER_CONTENT = __CHAPTER_JSON__;
const CHAPTERS = Object.keys(CHAPTER_CONTENT);

// 模拟班级数据
const CLASS_DATA = (function(){
  const names=['张明','李华','王芳','赵强','陈静','刘洋','周敏','吴磊','郑艳','孙涛','钱进','冯雪','褚明','卫红','蒋勇','沈悦','韩冰','杨帆','朱琳','秦峰','尤佳','许超','何丽','吕刚','施婷','张磊','孔颖','曹阳','严华','金鹏','魏丽','陶然','姜华','戚芳','谢明','邹强','喻红','柏亮','水静','窦明','章华','云芳','苏强','潘丽','葛明'];
  return names.map((n,i)=>({id:'2024'+String(i+1).padStart(3,'0'),name:n,
    regular:Math.round(70+Math.random()*28),
    mid:Math.round(55+Math.random()*40),
    final:Math.round(50+Math.random()*45),
    total:0})).map(s=>{s.total=Math.round(s.regular*0.3+s.mid*0.2+s.final*0.5);return s;});
})();

// ===== 状态 =====
const STORAGE_KEY='aviation_accounting_v2';
let state=loadState();
function loadState(){try{const s=JSON.parse(localStorage.getItem(STORAGE_KEY));return s||{answers:{},wrong:[],exams:[]};}catch(e){return{answers:{},wrong:[],exams:[]};}}
function saveState(){localStorage.setItem(STORAGE_KEY,JSON.stringify(state));}
function toast(msg,type='info'){const t=document.createElement('div');t.className='toast '+type;t.textContent=msg;document.getElementById('toastContainer').appendChild(t);setTimeout(()=>t.remove(),2500);}

// ===== 角色切换 =====
document.querySelectorAll('.role-tab').forEach(tab=>{
  tab.addEventListener('click',()=>{
    document.querySelectorAll('.role-tab').forEach(t=>t.classList.remove('active'));
    tab.classList.add('active');
    const role=tab.dataset.role;
    document.getElementById('studentNav').classList.toggle('hidden',role!=='student');
    document.getElementById('teacherNav').classList.toggle('hidden',role!=='teacher');
    // 切换到对应默认视图
    document.querySelectorAll('.view').forEach(v=>v.classList.add('hidden'));
    document.querySelectorAll('.nav-item').forEach(i=>i.classList.remove('active'));
    if(role==='student'){document.getElementById('view-dashboard').classList.remove('hidden');document.querySelector('[data-view="dashboard"]').classList.add('active');renderDashboard();}
    else{document.getElementById('view-t-dashboard').classList.remove('hidden');document.querySelector('[data-view="t-dashboard"]').classList.add('active');renderTeacherDashboard();}
  });
});

// ===== 路由 =====
document.querySelectorAll('.nav-item').forEach(item=>{
  item.addEventListener('click',()=>{
    document.querySelectorAll('.nav-item').forEach(i=>i.classList.remove('active'));
    item.classList.add('active');
    const view=item.dataset.view;
    document.querySelectorAll('.view').forEach(v=>v.classList.add('hidden'));
    document.getElementById('view-'+view).classList.remove('hidden');
    if(view==='dashboard')renderDashboard();
    if(view==='knowledge')renderKnowledge();
    if(view==='quiz')renderQuiz();
    if(view==='ai')renderAI();
    if(view==='score')renderScore();
    if(view==='wrong')renderWrong();
    if(view==='t-dashboard')renderTeacherDashboard();
    if(view==='t-bank')renderBank();
    if(view==='t-class')renderClass();
  });
});

// ===== 学生端：仪表盘 =====
function renderDashboard(){
  document.getElementById('statTotal').textContent=QUESTIONS.length;
  const answered=Object.keys(state.answers).length;
  const correct=Object.values(state.answers).filter(a=>a.correct).length;
  document.getElementById('statDone').textContent=answered;
  document.getElementById('statRate').textContent=answered>0?Math.round(correct/answered*100)+'%':'0%';
  document.getElementById('statWrong').textContent=state.wrong.length;
  document.getElementById('quizBadge').textContent=answered;
  const list=document.getElementById('chapterList');
  list.innerHTML='';
  CHAPTERS.forEach((ch,i)=>{
    const chQ=QUESTIONS.filter(q=>q.ch===ch);
    const chA=chQ.filter(q=>state.answers[q.id]).length;
    const chC=chQ.filter(q=>state.answers[q.id]?.correct).length;
    const rate=chA>0?Math.round(chC/chA*100):0;
    const item=document.createElement('div');
    item.className='chapter-item';
    item.innerHTML=`<div class="chapter-num">${i+1}</div><div class="chapter-info"><div class="title">${ch}</div><div class="meta">${CHAPTER_CONTENT[ch].hours} · ${chQ.length}题 · 已答${chA}题 · 正确率${rate}%</div></div><div class="chapter-progress"><div class="bar" style="width:${rate}%"></div></div><div style="color:var(--text-light);">›</div>`;
    item.addEventListener('click',()=>{document.querySelector('[data-view="knowledge"]').click();document.getElementById('knowledgeChapterSelect').querySelector('select').value=ch;showKnowledgeChapter(ch);});
    list.appendChild(item);
  });
}

// ===== 知识学习 =====
function renderKnowledge(){
  const sel=document.getElementById('knowledgeChapterSelect');
  sel.innerHTML='<select class="filter-btn active" id="chapterSelect" style="min-width:220px;">'+CHAPTERS.map(ch=>`<option value="${ch}">${ch}</option>`).join('')+'</select>';
  document.getElementById('chapterSelect').addEventListener('change',e=>showKnowledgeChapter(e.target.value));
  showKnowledgeChapter(CHAPTERS[0]);
}
function showKnowledgeChapter(ch){
  const k=CHAPTER_CONTENT[ch];
  document.getElementById('knowledgeContent').innerHTML=`<h3 style="margin-bottom:6px;">${ch}（${k.hours}）</h3><p style="color:var(--text-light);font-size:12px;margin-bottom:14px;">核心知识点：${k.kp.join(' · ')}</p><div class="knowledge-content">${k.content}</div>`;
}

// ===== 智能练习 =====
let quizFilter={chapter:'全部',type:'全部'};
function renderQuiz(){
  const chF=document.getElementById('chapterFilter');
  chF.innerHTML='<span style="font-size:12px;color:var(--text-light);">章节：</span>'+['全部',...CHAPTERS].map(ch=>`<button class="filter-btn ${quizFilter.chapter===ch?'active':''}" data-ch="${ch}">${ch==='全部'?'全部':ch.replace('第','').replace('章 ','')}</button>`).join('');
  chF.querySelectorAll('[data-ch]').forEach(b=>b.addEventListener('click',()=>{quizFilter.chapter=b.dataset.ch;renderQuiz();}));
  const types=['全部','单选题','多选题','判断题','分录题','计算分析题','简答题','名词解释','案例题'];
  const tF=document.getElementById('typeFilter');
  tF.innerHTML='<span style="font-size:12px;color:var(--text-light);">题型：</span>'+types.map(t=>`<button class="filter-btn ${quizFilter.type===t?'active':''}" data-type="${t}">${t}</button>`).join('');
  tF.querySelectorAll('[data-type]').forEach(b=>b.addEventListener('click',()=>{quizFilter.type=b.dataset.type;renderQuiz();}));
  let list=QUESTIONS;
  if(quizFilter.chapter!=='全部')list=list.filter(q=>q.ch===quizFilter.chapter);
  if(quizFilter.type!=='全部')list=list.filter(q=>q.type===quizFilter.type);
  const ql=document.getElementById('quizList');
  if(list.length===0){ql.innerHTML='<div class="card"><p style="text-align:center;color:var(--text-light);">该筛选条件下暂无题目</p></div>';return;}
  ql.innerHTML=list.map(q=>renderQuizCard(q)).join('');
  list.forEach(q=>bindQuizEvents(q));
}

function renderQuizCard(q){
  const diffClass=q.diff==='易'?'diff-easy':q.diff==='中'?'diff-mid':'diff-hard';
  const isObjective=['单选题','多选题','判断题'].includes(q.type);
  const optLabels=['A','B','C','D'];
  let optionsHtml='';
  if(isObjective){
    const opts=[q.A,q.B,q.C,q.D].filter(o=>o&&o.trim()!=='');
    optionsHtml=`<div class="quiz-options">${opts.map((o,i)=>`<div class="quiz-option" data-opt="${optLabels[i]}"><span class="opt-label">${optLabels[i]}</span>${o}</div>`).join('')}</div>`;
  }else{
    optionsHtml=`<textarea class="subjective-area" placeholder="请输入你的答案（分录题请写借贷分录，计算题请写计算过程）..."></textarea>`;
  }
  return `<div class="quiz-card" id="quiz-${q.id}">
    <div class="quiz-meta"><span class="tag chapter">${q.ch}</span><span class="tag type">${q.type}</span><span class="tag ${diffClass}">${q.diff}</span>${q.aviation==='是'?'<span class="tag aviation">民航特色</span>':''}<span style="margin-left:auto;font-size:11px;color:var(--text-light);">${q.kp} · ${q.score}分</span></div>
    <div class="quiz-question">${q.q}</div>${optionsHtml}
    <div class="quiz-actions"><button class="btn btn-primary btn-submit">${isObjective?'提交答案':'提交并初评'}</button></div>
    <div class="quiz-result"></div></div>`;
}

function bindQuizEvents(q){
  const card=document.getElementById('quiz-'+q.id);
  if(!card)return;
  const isObjective=['单选题','多选题','判断题'].includes(q.type);
  let selected=[];
  if(isObjective){
    const options=card.querySelectorAll('.quiz-option');
    options.forEach(opt=>{
      opt.addEventListener('click',()=>{
        if(q.type==='多选题'){opt.classList.toggle('selected');selected=Array.from(card.querySelectorAll('.quiz-option.selected')).map(o=>o.dataset.opt);}
        else{options.forEach(o=>o.classList.remove('selected'));opt.classList.add('selected');selected=[opt.dataset.opt];}
      });
    });
  }
  card.querySelector('.btn-submit').addEventListener('click',()=>{
    const result=card.querySelector('.quiz-result');
    let isCorrect=false,score=0,maxScore=parseInt(q.score)||10;
    if(isObjective){
      if(selected.length===0){toast('请先选择答案','error');return;}
      const userAnswer=selected.sort().join('');
      isCorrect=userAnswer===q.answer;
      score=isCorrect?maxScore:0;
      const options=card.querySelectorAll('.quiz-option');
      options.forEach(o=>{if(q.answer.includes(o.dataset.opt))o.classList.add('correct');if(selected.includes(o.dataset.opt)&&!q.answer.includes(o.dataset.opt))o.classList.add('wrong');});
      result.classList.add('show',isCorrect?'correct':'wrong');
      result.innerHTML=`<div class="result-title">${isCorrect?'✓ 回答正确（+'+maxScore+'分）':'✗ 回答错误'}</div><div>你的答案：${selected.join('、')} | 正确答案：${q.answer.split('').join('、')}</div><div class="result-explain">解析：${q.explain}</div>`;
    }else{
      // 主观题关键词匹配初评
      const textarea=card.querySelector('.subjective-area');
      const userText=textarea.value.trim();
      if(userText===''){toast('请先输入答案','error');return;}
      const keywords=q.keywords||[];
      if(keywords.length===0){
        // 无关键词时用长度和相似度粗略评估
        const refLen=(q.explain||'').length;
        const ratio=Math.min(userText.length/refLen,1);
        score=Math.round(maxScore*ratio*0.7);
        isCorrect=score>=maxScore*0.6;
      }else{
        let matched=0;
        keywords.forEach(kw=>{if(userText.includes(kw))matched++;});
        const matchRate=matched/keywords.length;
        score=Math.round(maxScore*matchRate);
        isCorrect=matchRate>=0.6;
      }
      const pct=Math.round(score/maxScore*100);
      result.classList.add('show',isCorrect?'correct':'partial');
      result.innerHTML=`<div class="result-title">${isCorrect?'✓ 初评通过（'+score+'/'+maxScore+'分）':'◐ 需完善（'+score+'/'+maxScore+'分，'+pct+'%）'}</div>
        <div style="margin:6px 0;">关键词匹配：${keywords.filter(k=>userText.includes(k)).length}/${keywords.length}个 ${keywords.filter(k=>userText.includes(k)).map(k=>'<span class="tag type" style="margin:0 2px;">'+k+'</span>').join('')}</div>
        <div class="result-explain"><strong>参考答案：</strong>${q.explain}</div>
        <div style="font-size:11px;color:var(--text-light);margin-top:6px;">* 主观题为关键词匹配初评，最终成绩以教师复核为准</div>`;
    }
    state.answers[q.id]={correct:isCorrect,score:score,maxScore:maxScore,chapter:q.ch,kp:q.kp,type:q.type};
    if(!isCorrect&&!state.wrong.includes(q.id))state.wrong.push(q.id);
    if(isCorrect)state.wrong=state.wrong.filter(id=>id!==q.id);
    saveState();
    card.querySelector('.btn-submit').disabled=true;
    card.querySelector('.btn-submit').textContent='已提交';
  });
}

// ===== AI答疑（RAG检索增强 + 可选真实LLM后端）=====
let AI_BACKEND_AVAILABLE=null;
const AI_FAQ={
  '航油成本占比多少':['航油成本通常是航空公司最大的单一成本项目，占营业成本的25%-35%，甚至更高。','它受国际油价、航线结构、机队燃油效率、航距等多因素影响。'],
  '飞机租赁一般采用说明方式':['飞机租赁在民航会计中通常采用融资租赁或经营租赁两种方式。','融资租赁需确认使用权资产和租赁负债，按实际利率法计提折旧和利息；经营租赁则将租金按直线法计入当期成本费用。'],
  '飞机折旧为什么用两种方法':['飞机折旧常结合年限平均法（直线法）和飞行小时法。','直线法按预计使用年限平均分摊；飞行小时法按实际飞行小时与预计总飞行小时比例分摊，更匹配航空资产的使用强度。'],
  '常旅客里程怎么确认收入':['常旅客奖励里程在授予时按公允价值计入递延收益（合同负债）。','待会员实际兑换并使用里程时，再按比例确认为运输收入。'],
  '什么是BSP结算':['BSP（Billing and Settlement Plan，开账与结算计划）是IATA推出的全球航空客票销售结算系统。','它通过中性票证和统一结算，简化航空公司与代理人之间的票款清算。'],
  'C检费用资本化还是费用化':['例行C检等定期检查通常按计划维修费用资本化或按受益期摊销。','具体需结合企业会计政策和C检支出的经济实质判断：若形成未来经济利益则资本化，否则费用化。']
};
async function checkAIStatus(){
  const badge=document.getElementById('aiStatus');
  try{
    const r=await fetch('http://localhost:8000/api/config',{method:'GET',signal:AbortSignal.timeout(2500)});
    const j=await r.json();
    AI_BACKEND_AVAILABLE=!!j.configured;
    if(badge){badge.className='ai-status '+(AI_BACKEND_AVAILABLE?'online':'offline');badge.textContent=AI_BACKEND_AVAILABLE?'LLM 在线':'本地模式';}
  }catch(e){
    AI_BACKEND_AVAILABLE=false;
    if(badge){badge.className='ai-status offline';badge.textContent='本地模式';}
  }
}
function renderAI(){
  const msgs=document.getElementById('aiMessages');
  if(msgs.children.length===0){
    msgs.innerHTML=`<div class="ai-msg bot">你好！我是民航会计AI答疑助手，基于民航运输企业会计知识库为你解答问题。你可以问我关于飞机折旧、常旅客计划、航油成本、票证结算、飞机租赁等任何民航会计问题。本地模式下使用知识库RAG；若启动本地LLM代理，可获得更强的生成式回答。</div>`;
  }
  const sug=document.getElementById('aiSuggestions');
  const suggestions=['飞机折旧为什么用两种方法？','常旅客里程怎么确认收入？','航油成本占比多少？','什么是BSP结算？','使用权资产怎么计量？','C检费用资本化还是费用化？'];
  sug.innerHTML=suggestions.map(s=>`<span class="ai-suggestion" onclick="document.getElementById('aiInput').value='${s}';sendAI();">${s}</span>`).join('');
  if(AI_BACKEND_AVAILABLE===null)checkAIStatus();
}
async function sendAI(){
  const input=document.getElementById('aiInput');
  const q=input.value.trim();
  if(!q)return;
  const msgs=document.getElementById('aiMessages');
  msgs.innerHTML+=`<div class="ai-msg user">${q}</div>`;
  input.value='';
  msgs.scrollTop=msgs.scrollHeight;
  const loadingId='ai-loading-'+Date.now();
  msgs.innerHTML+=`<div class="ai-msg bot" id="${loadingId}">正在思考……</div>`;
  msgs.scrollTop=msgs.scrollHeight;
  let answer=null;
  // 优先尝试真实LLM后端
  if(AI_BACKEND_AVAILABLE!==false){
    try{
      const r=await fetch('http://localhost:8000/api/chat',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({message:q,source:'aviation-mvp'}),
        signal:AbortSignal.timeout(20000)
      });
      if(r.ok){
        const j=await r.json();
        answer={text:j.answer||j.text||'(无返回)',sources:j.sources||['LLM生成']};
        AI_BACKEND_AVAILABLE=true;
      }
    }catch(e){AI_BACKEND_AVAILABLE=false;}
  }
  if(!answer) answer=ragSearch(q);
  document.getElementById(loadingId).outerHTML=`<div class="ai-msg bot">${answer.text}<div class="src">📚 来源：${answer.sources.join(' · ')}</div></div>`;
  msgs.scrollTop=msgs.scrollHeight;
}
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&document.activeElement.id==='aiInput')sendAI();});

function expandQuery(query){
  const synonyms={
    '折旧':['折旧','折旧方法','depreciation','损耗','年限平均','直线法','飞行小时法'],
    '租赁':['租赁','融资租赁','经营租赁','使用权资产','租赁负债','租金'],
    '航油':['航油','燃油','油料','航空煤油','燃油成本','油料成本'],
    '收入':['收入','确认收入','营业收入','运输收入','客运收入','货运收入'],
    'BSP':['BSP','开账与结算计划','票款结算','代理人结算','票证结算'],
    'C检':['C检','定期检查','维修','大修','资本化','费用化'],
    '常旅客':['常旅客','里程','奖励里程','递延收益','合同负债','积分']
  };
  const words=query.split(/[\s，。？、！；：.?!;:]+/).filter(w=>w.length>=2);
  const expanded=new Set(words);
  words.forEach(w=>{
    for(const k in synonyms){ if(w.includes(k)||k.includes(w)) synonyms[k].forEach(s=>expanded.add(s)); }
  });
  return Array.from(expanded);
}
function scoreKB(query,kb,qWords){
  let score=0;
  const text=(kb.chapter||'')+' '+(kb.title||'')+' '+(kb.content||'')+' '+(kb.keywords?kb.keywords.join(' '):'');
  const lower=text.toLowerCase();
  const qlower=query.toLowerCase();
  // 整词命中标题权重高
  kb.keywords.forEach(kw=>{ if(qlower.includes(kw.toLowerCase())) score+=5; });
  // 分词在内容中出现
  qWords.forEach(w=>{
    if(kb.title.toLowerCase().includes(w.toLowerCase())) score+=3;
    if(lower.includes(w.toLowerCase())) score+=2;
  });
  return score;
}
function ragSearch(query){
  // 1. 优先FAQ
  const qKey=Object.keys(AI_FAQ).find(k=>query.toLowerCase().includes(k.toLowerCase()));
  if(qKey){
    return{text:'<p>'+AI_FAQ[qKey].join('</p><p>')+'</p>',sources:['常见问题库']};
  }
  // 2. 知识库检索
  const qWords=expandQuery(query);
  let scored=KNOWLEDGE_BASE.map(kb=>{return{...kb,score:scoreKB(query,kb,qWords)}}).filter(k=>k.score>0).sort((a,b)=>b.score-a.score);
  if(scored.length===0){
    // 3. 题目解析 fallback
    const qlower=query.toLowerCase();
    const matchedQ=QUESTIONS.filter(q=>q.explain&&q.explain.length>10).sort((a,b)=>{
      const ta=(a.q||'')+' '+(a.explain||''); const tb=(b.q||'')+' '+(b.explain||'');
      let sa=0,sb=0; qWords.forEach(w=>{ if(ta.toLowerCase().includes(w.toLowerCase())) sa++; if(tb.toLowerCase().includes(w.toLowerCase())) sb++; });
      return sb-sa;
    })[0];
    if(matchedQ && qWords.some(w=>(matchedQ.q+matchedQ.explain).toLowerCase().includes(w.toLowerCase()))){
      return{text:`<p>根据题库中「${matchedQ.ch}」的${matchedQ.type}，可参考以下解析：</p><blockquote>${matchedQ.explain}</blockquote><p>若需针对具体场景深入分析，可补充背景后再次提问。</p>`,sources:['题库-'+matchedQ.id]};
    }
    return{text:'<p>抱歉，我在知识库和题库中暂未找到与该问题直接匹配的内容。建议尝试：</p><ul><li>换一种更具体的问法，例如「融资租赁飞机的折旧方法」；</li><li>点击上方常见问题快速体验；</li><li>启动本地LLM代理后，模型可基于知识库生成更开放的回答。</li></ul>',sources:['知识库未命中']};
  }
  const top=scored.slice(0,3);
  const text='<p>根据民航运输企业会计知识库，为您整理以下要点：</p>'+top.map((k,i)=>`<p><strong>${i+1}. ${k.title}</strong><br>${k.content}</p>`).join('')+'<p style="font-size:12px;color:var(--text-light)">以上基于教材与题库知识库，仅供参考。</p>';
  return{text:text,sources:top.map(k=>k.chapter+'·'+k.title)};
}

// ===== 成绩分析 =====
function renderScore(){
  const answered=Object.keys(state.answers).length;
  const correct=Object.values(state.answers).filter(a=>a.correct).length;
  document.getElementById('totalAnswered').textContent=answered;
  document.getElementById('totalCorrect').textContent=correct;
  document.getElementById('overallRate').textContent=answered>0?Math.round(correct/answered*100)+'%':'0%';
  const cs=document.getElementById('chapterScores');
  cs.innerHTML=CHAPTERS.map(ch=>{
    const qs=QUESTIONS.filter(q=>q.ch===ch);
    const ans=qs.filter(q=>state.answers[q.id]);
    const cor=ans.filter(q=>state.answers[q.id].correct).length;
    const rate=ans.length>0?Math.round(cor/ans.length*100):0;
    const color=rate>=80?'var(--success)':rate>=60?'var(--warning)':'var(--danger)';
    return `<div class="chapter-score-row"><div class="cs-name">${ch}</div><div class="cs-bar"><div class="cs-fill" style="width:${rate}%;background:${color};"></div></div><div class="cs-score" style="color:${color}">${ans.length>0?rate+'%':'未答'}</div></div>`;
  }).join('');
  const kpStats={};
  Object.values(state.answers).forEach(a=>{if(!kpStats[a.kp])kpStats[a.kp]={total:0,correct:0};kpStats[a.kp].total++;if(a.correct)kpStats[a.kp].correct++;});
  const kpEl=document.getElementById('kpMastery');
  const entries=Object.entries(kpStats).sort((a,b)=>(a[1].correct/a[1].total)-(b[1].correct/b[1].total));
  if(entries.length===0){kpEl.innerHTML='<p style="color:var(--text-light);">暂无答题数据</p>';return;}
  kpEl.innerHTML=entries.map(([kp,s])=>{const rate=Math.round(s.correct/s.total*100);const status=rate>=80?'掌握良好':rate>=60?'基本掌握':'需要加强';const color=rate>=80?'var(--success)':rate>=60?'var(--warning)':'var(--danger)';return `<div class="chapter-score-row"><div class="cs-name">${kp}</div><div class="cs-bar"><div class="cs-fill" style="width:${rate}%;background:${color};"></div></div><div class="cs-score" style="color:${color};font-size:11px;">${status}(${rate}%)</div></div>`;}).join('');
}

// ===== 错题本 =====
function renderWrong(){
  const list=document.getElementById('wrongList');
  if(state.wrong.length===0){list.innerHTML='<div class="card"><p style="text-align:center;color:var(--success);">太棒了！暂无错题</p></div>';return;}
  list.innerHTML=state.wrong.map(id=>{
    const q=QUESTIONS.find(x=>x.id===id);if(!q)return '';
    const ans=state.answers[id];
    return `<div class="wrong-item"><div class="wq"><strong>${q.ch} · ${q.type}</strong> ${q.q}</div><div class="wa">${ans?.userAnswer?'你的答案：'+ans.userAnswer+' | ':''}正确答案：${q.answer}</div><div class="wa" style="margin-top:4px;color:var(--text);">解析：${q.explain}</div><button class="btn btn-outline btn-sm" style="margin-top:8px;" onclick="removeWrong('${id}')">已掌握，移除</button></div>`;
  }).join('');
}
function removeWrong(id){state.wrong=state.wrong.filter(w=>w!==id);saveState();renderWrong();toast('已从错题本移除','success');}

// ===== 教师端：教学概览 =====
function renderTeacherDashboard(){
  document.getElementById('tTotal').textContent=QUESTIONS.length;
  const rates=CLASS_DATA.map(s=>s.total);
  const avg=Math.round(rates.reduce((a,b)=>a+b,0)/rates.length);
  document.getElementById('tAvgRate').textContent=avg+'%';
  document.getElementById('tExamCount').textContent=state.exams.length;
  // 题库分布
  const typeCount={};
  QUESTIONS.forEach(q=>{typeCount[q.type]=(typeCount[q.type]||0)+1;});
  document.getElementById('bankDistribution').innerHTML=Object.entries(typeCount).map(([t,c])=>`<div class="chapter-score-row"><div class="cs-name">${t}</div><div class="cs-bar"><div class="cs-fill" style="width:${c/QUESTIONS.length*100}%;background:var(--primary);"></div></div><div class="cs-score">${c}题</div></div>`).join('');
  // 班级成绩分布
  const ranges=['0-59','60-69','70-79','80-89','90-100'];
  const counts=ranges.map(r=>{const[lo,hi]=r.split('-').map(Number);return CLASS_DATA.filter(s=>s.total>=lo&&s.total<=hi).length;});
  const maxC=Math.max(...counts,1);
  document.getElementById('classChart').innerHTML=ranges.map((r,i)=>`<div class="bar-item"><div class="bar" style="height:${counts[i]/maxC*200}px;"><span class="bar-val">${counts[i]}</span></div><div class="bar-label">${r}</div></div>`).join('');
}

// ===== 教师端：题库管理 =====
let bankFilter={chapter:'全部',type:'全部'};
function renderBank(){
  const chF=document.getElementById('bankChapterFilter');
  chF.innerHTML='<span style="font-size:12px;color:var(--text-light);">章节：</span>'+['全部',...CHAPTERS].map(ch=>`<button class="filter-btn ${bankFilter.chapter===ch?'active':''}" data-bch="${ch}">${ch==='全部'?'全部':ch.replace('第','').replace('章 ','')}</button>`).join('');
  chF.querySelectorAll('[data-bch]').forEach(b=>b.addEventListener('click',()=>{bankFilter.chapter=b.dataset.bch;renderBank();}));
  const types=['全部','单选题','多选题','判断题','分录题','计算分析题','简答题','名词解释','案例题'];
  const tF=document.getElementById('bankTypeFilter');
  tF.innerHTML='<span style="font-size:12px;color:var(--text-light);">题型：</span>'+types.map(t=>`<button class="filter-btn ${bankFilter.type===t?'active':''}" data-btype="${t}">${t}</button>`).join('');
  tF.querySelectorAll('[data-btype]').forEach(b=>b.addEventListener('click',()=>{bankFilter.type=b.dataset.btype;renderBank();}));
  let list=QUESTIONS;
  if(bankFilter.chapter!=='全部')list=list.filter(q=>q.ch===bankFilter.chapter);
  if(bankFilter.type!=='全部')list=list.filter(q=>q.type===bankFilter.type);
  document.getElementById('bankCount').textContent=list.length;
  const tbody=document.querySelector('#bankTable tbody');
  tbody.innerHTML=list.slice(0,100).map(q=>`<tr><td>${q.id}</td><td>${q.ch.replace('第','').replace('章 ','')}</td><td>${q.type}</td><td>${q.diff}</td><td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${q.q}</td><td>${q.score}</td><td>${q.aviation==='是'?'✓':''}</td></tr>`).join('');
  if(list.length>100)tbody.innerHTML+=`<tr><td colspan="7" style="text-align:center;color:var(--text-light);">仅显示前100条，共${list.length}条，请使用筛选缩小范围</td></tr>`;
}

// ===== 教师端：自动组卷 =====
function generateExam(){
  const name=document.getElementById('examName').value;
  const duration=document.getElementById('examDuration').value;
  const chapter=document.getElementById('examChapter').value;
  const diff=document.getElementById('examDiff').value;
  const nSingle=parseInt(document.getElementById('nSingle').value)||0;
  const nMulti=parseInt(document.getElementById('nMulti').value)||0;
  const nJudge=parseInt(document.getElementById('nJudge').value)||0;
  const nSubj=parseInt(document.getElementById('nSubj').value)||0;
  let pool=QUESTIONS;
  if(chapter!=='全部')pool=pool.filter(q=>q.ch===chapter);
  // 难度权重
  const diffWeight={balanced:{易:3,中:5,难:2},easy:{易:5,中:4,难:1},hard:{易:1,中:4,难:5}}[diff];
  function pick(type,count){
    let candidates=pool.filter(q=>q.type===type);
    // 按难度加权随机
    const weighted=[];
    candidates.forEach(q=>{const w=diffWeight[q.diff]||1;for(let i=0;i<w;i++)weighted.push(q);});
    const picked=[];const used=new Set();
    for(let i=0;i<count&&weighted.length>0;i++){
      let tries=0;
      while(tries<20){const idx=Math.floor(Math.random()*weighted.length);const q=weighted[idx];if(!used.has(q.id)){picked.push(q);used.add(q.id);break;}tries++;}
    }
    return picked;
  }
  const exam=[...pick('单选题',nSingle),...pick('多选题',nMulti),...pick('判断题',nJudge),
    ...pick('分录题',Math.ceil(nSubj*0.4)),...pick('计算分析题',Math.ceil(nSubj*0.3)),
    ...pick('简答题',Math.ceil(nSubj*0.2)),...pick('名词解释',Math.ceil(nSubj*0.1)),...pick('案例题',1)];
  const totalScore=exam.reduce((s,q)=>s+(parseInt(q.score)||0),0);
  const examData={name,duration,chapter,questions:exam.map(q=>q.id),totalScore,createdAt:new Date().toLocaleString()};
  state.exams.push(examData);saveState();
  // 预览
  const result=document.getElementById('examResult');
  result.classList.remove('hidden');
  document.getElementById('examPreview').innerHTML=`
    <div style="margin-bottom:14px;padding:12px;background:var(--primary-light);border-radius:8px;">
      <strong>${name}</strong> · 时长${duration}分钟 · 共${exam.length}题 · 总分${totalScore}分 · ${chapter==='全部'?'全部章节':chapter}
    </div>
    ${exam.map((q,i)=>`<div class="exam-q"><span class="eq-num">${i+1}.</span>【${q.type}·${q.score}分】${q.q}${q.A?`<div style="margin-top:6px;padding-left:20px;font-size:12px;color:var(--text-light);">A.${q.A} B.${q.B}${q.C?' C.':''}${q.C||''}${q.D?' D.':''}${q.D||''}</div>`:''}<div style="margin-top:4px;font-size:11px;color:var(--text-light);">答案：${q.answer} | ${q.ch}</div></div>`).join('')}`;
  toast(`试卷生成成功！共${exam.length}题，${totalScore}分`,'success');
}
function exportExam(){
  if(state.exams.length===0){toast('请先生成试卷','error');return;}
  const exam=state.exams[state.exams.length-1];
  const qs=exam.questions.map(id=>QUESTIONS.find(q=>q.id===id)).filter(Boolean);
  let text=`${exam.name}\n时长：${exam.duration}分钟  总分：${exam.totalScore}分\n\n`;
  qs.forEach((q,i)=>{text+=`${i+1}.【${q.type}】${q.q}（${q.score}分）\n`;if(q.A)text+=`  A.${q.A}  B.${q.B}  C.${q.C||''}  D.${q.D||''}\n`;text+=`\n参考答案：${q.answer}\n解析：${q.explain}\n\n`;});
  const blob=new Blob([text],{type:'text/plain;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=exam.name+'.txt';a.click();
  toast('试卷已导出','success');
}

// ===== 教师端：班级成绩 =====
function renderClass(){
  // 成绩分布
  const ranges=['0-59','60-69','70-79','80-89','90-100'];
  const counts=ranges.map(r=>{const[lo,hi]=r.split('-').map(Number);return CLASS_DATA.filter(s=>s.total>=lo&&s.total<=hi).length;});
  const maxC=Math.max(...counts,1);
  document.getElementById('scoreDistChart').innerHTML=ranges.map((r,i)=>`<div class="bar-item"><div class="bar" style="height:${counts[i]/maxC*220}px;"><span class="bar-val">${counts[i]}</span></div><div class="bar-label">${r}</div></div>`).join('');
  // 排名表
  const sorted=[...CLASS_DATA].sort((a,b)=>b.total-a.total);
  const tbody=document.querySelector('#classRankTable tbody');
  tbody.innerHTML=sorted.map((s,i)=>{const grade=s.total>=90?'优':s.total>=80?'良':s.total>=70?'中':s.total>=60?'及格':'不及格';const color=s.total>=90?'var(--success)':s.total>=60?'var(--primary)':'var(--danger)';return `<tr><td>${i+1}</td><td>${s.id}</td><td>${s.name}</td><td>${s.regular}</td><td>${s.mid}</td><td>${s.final}</td><td><strong>${s.total}</strong></td><td style="color:${color};font-weight:600;">${grade}</td></tr>`;}).join('');
  // 各章班级正确率（模拟）
  const chapterRates=CHAPTERS.map((ch,i)=>({ch,rate:Math.round(55+Math.random()*40)}));
  document.getElementById('classChapterRate').innerHTML=chapterRates.map(c=>{const color=c.rate>=80?'var(--success)':c.rate>=60?'var(--warning)':'var(--danger)';return `<div class="chapter-score-row"><div class="cs-name">${c.ch}</div><div class="cs-bar"><div class="cs-fill" style="width:${c.rate}%;background:${color};"></div></div><div class="cs-score" style="color:${color}">${c.rate}%</div></div>`;}).join('');
}

// 初始化
renderDashboard();
</script>
</body>
</html>'''

# 合并旧版物流题库补充的章节与知识库（若存在，不强制）
try:
    with open(os.path.join(_BASE, 'chapter_content_extra.json'), encoding='utf-8') as _f:
        CHAPTER_CONTENT.update(json.load(_f))
except FileNotFoundError:
    pass
try:
    with open(os.path.join(_BASE, 'kb_extra.json'), encoding='utf-8') as _f:
        KNOWLEDGE_BASE.extend(json.load(_f))
except FileNotFoundError:
    pass

# 替换占位符
chapter_options = ''.join(f'<option value="{ch}">{ch}</option>' for ch in CHAPTER_CONTENT.keys())
html = html_template.replace('__CHAPTER_OPTIONS__', chapter_options)
html = html.replace('__QUESTIONS_JSON__', json.dumps(questions, ensure_ascii=False, indent=2))
html = html.replace('__KB_JSON__', json.dumps(KNOWLEDGE_BASE, ensure_ascii=False, indent=2))
html = html.replace('__CHAPTER_JSON__', json.dumps(CHAPTER_CONTENT, ensure_ascii=False, indent=2))

output_path = os.path.join(_BASE, 'index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"MVP v2.0 已生成: {output_path}")
print(f"文件大小: {len(html)} 字节")
print(f"题库: {len(questions)}题")
print(f"知识库: {len(KNOWLEDGE_BASE)}条")
print(f"章节: {len(CHAPTER_CONTENT)}章")
