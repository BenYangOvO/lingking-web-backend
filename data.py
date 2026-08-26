"""静态数据 - 摄影社团内容（零依赖，纯 Python 数据结构）"""

PHOTOS = [
    {"id": 1, "title": "晨光中的城市", "author": "张明远", "likes": 128, "cat": "风光", "grad": "#2D5F8A,#4A90D9,#6AADE8"},
    {"id": 2, "title": "雨后巷弄", "author": "李思琪", "likes": 96, "cat": "街拍", "grad": "#0F766E,#14B8A6,#5EEAD4"},
    {"id": 3, "title": "星空下的远山", "author": "王浩宇", "likes": 214, "cat": "风光", "grad": "#1E1B4B,#312E81,#4F46E5,#818CF8"},
    {"id": 4, "title": "秋日暖阳", "author": "陈雨薇", "likes": 87, "cat": "风光", "grad": "#78350F,#B45309,#F59E0B,#FCD34D"},
    {"id": 5, "title": "海边的黄昏", "author": "林子涵", "likes": 175, "cat": "风光", "grad": "#0C4A6E,#0284C7,#38BDF8,#7DD3FC"},
    {"id": 6, "title": "老街记忆", "author": "赵一凡", "likes": 143, "cat": "纪实", "grad": "#1C1917,#44403C,#78716C,#A8A29E"},
    {"id": 7, "title": "光影交错", "author": "周思远", "likes": 109, "cat": "创意", "grad": "#7C2D12,#C2410C,#FB923C,#FDBA74"},
    {"id": 8, "title": "静物之美", "author": "孙晓婷", "likes": 76, "cat": "纪实", "grad": "#134E4A,#0D9488,#2DD4BF,#99F6E4"},
    {"id": 9, "title": "霓虹夜色", "author": "黄乐天", "likes": 201, "cat": "创意", "grad": "#3B0764,#7E22CE,#A855F7,#C084FC"},
    {"id": 10, "title": "山间云海", "author": "吴昊然", "likes": 162, "cat": "风光", "grad": "#14532D,#16A34A,#4ADE80,#86EFAC"},
    {"id": 11, "title": "城市天际线", "author": "郑雨萱", "likes": 135, "cat": "建筑", "grad": "#1E3A5F,#4A90D9,#7DD3FC,#BAE6FD"},
    {"id": 12, "title": "花间人像", "author": "刘诗雅", "likes": 188, "cat": "人像", "grad": "#881337,#E11D48,#FB7185,#FDA4AF"},
]

MEMBERS = [
    {"id": 1, "name": "林若曦", "nickname": "小曦光", "dept": "摄影部", "bio": "永远在找光", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #C4B5FD, #A78BFA, #DDD6FE)", "color": "#5B21B6"},
    {"id": 2, "name": "陈逸飞", "nickname": "像素猎人", "dept": "技术部", "bio": "修图狂魔", "happy": False, "smile": False, "bg": "linear-gradient(135deg, #BAE6FD, #7DD3FC, #E0F2FE)", "color": "#0369A1"},
    {"id": 3, "name": "苏雨晴", "nickname": "快门少女", "dept": "摄影部", "bio": "快门杀手", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #FBCFE8, #F9A8D4, #FCE7F3)", "color": "#9D174D"},
    {"id": 4, "name": "赵明轩", "nickname": "构图大师", "dept": "摄影部", "bio": "构图强迫症", "happy": False, "smile": False, "bg": "linear-gradient(135deg, #BBF7D0, #86EFAC, #DCFCE7)", "color": "#166534"},
    {"id": 5, "name": "周艺凡", "nickname": "魔法师", "dept": "技术部", "bio": "后期魔法师", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #FEF08A, #FDE047, #FEF9C3)", "color": "#854D0E"},
    {"id": 6, "name": "吴天佑", "nickname": "器材控", "dept": "摄影部", "bio": "镜头收藏家", "happy": False, "smile": False, "bg": "linear-gradient(135deg, #FED7AA, #FDBA74, #FFEDD5)", "color": "#9A3412"},
    {"id": 7, "name": "许晨光", "nickname": "追光者", "dept": "宣传部", "bio": "日出猎人", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #99F6E4, #5EEAD4, #CCFBF1)", "color": "#115E59"},
    {"id": 8, "name": "方梓涵", "nickname": "调色侠", "dept": "技术部", "bio": "色彩感知者", "happy": False, "smile": False, "bg": "linear-gradient(135deg, #FECDD3, #FDA4AF, #FFE4E6)", "color": "#9F1239"},
    {"id": 9, "name": "孙晓婷", "nickname": "文艺婷", "dept": "宣传部", "bio": "文案撰写与视觉设计", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #FECACA, #FCA5A5, #FEE2E2)", "color": "#991B1B"},
    {"id": 10, "name": "黄乐天", "nickname": "夜行者", "dept": "摄影部", "bio": "夜景与创意摄影", "happy": False, "smile": False, "bg": "linear-gradient(135deg, #C4B5FD, #A78BFA, #DDD6FE)", "color": "#5B21B6"},
    {"id": 11, "name": "郑雨萱", "nickname": "建筑眼", "dept": "技术部", "bio": "建筑摄影与后期处理", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #A5F3FC, #67E8F9, #CFFAFE)", "color": "#155E75"},
    {"id": 12, "name": "刘诗雅", "nickname": "花仙子", "dept": "宣传部", "bio": "人像摄影与社交媒体运营", "happy": True, "smile": True, "bg": "linear-gradient(135deg, #FBCFE8, #F9A8D4, #FCE7F3)", "color": "#9D174D"},
]

DEPARTMENTS = [
    {"id": 1, "name": "摄影部", "desc": "负责社团核心摄影创作，包括外拍活动策划、主题拍摄项目以及日常创作交流。从人像到风光，从纪实到创意，这里汇聚了社团最活跃的摄影师。", "count": 80, "icon": "camera"},
    {"id": 2, "name": "技术部", "desc": "专注于后期处理、视频剪辑与新媒体技术。提供 Lightroom、Photoshop、Premiere 等软件的教学与指导，助力成员提升作品品质。", "count": 60, "icon": "monitor"},
    {"id": 3, "name": "宣传部", "desc": "负责社团品牌运营与对外宣传，包括社交媒体管理、活动文案撰写、海报设计与线上展览策划，是社团对外发声的重要窗口。", "count": 55, "icon": "megaphone"},
]

DIARY_ENTRIES = [
    {"id": 1, "date": "2026-07-15", "title": "凌晨四点的日出", "mood": "震撼", "mood_class": "mood-wonder", "tag": "摄影心得", "excerpt": "为了拍下这张日出，我在凌晨三点爬上了山顶。当第一缕阳光穿透云层的那一刻，所有的困倦和寒冷都烟消云散了。镜头里的世界仿佛被重新涂上了一层金色的油彩，那种宁静而壮丽的感觉，是任何后期都无法复刻的。摄影教会我，有些美好只属于愿意等待的人。", "author": "王浩宇", "avatar": "王", "avatar_bg": "linear-gradient(135deg,#4A90D9,#6AADE8)", "read_time": "8 分钟阅读", "likes": 214, "comments": 36, "bg": "linear-gradient(145deg,#1E3A5F,#2D5F8A,#4A90D9,#6AADE8)"},
    {"id": 2, "date": "2026-07-10", "title": "雨后的校园", "mood": "宁静", "mood_class": "mood-peaceful", "tag": "拍摄日记", "excerpt": "夏天的雨来得快去得也快。雨停之后，校园里的每一片叶子都挂着晶莹的水珠，倒映着天光。我喜欢在这样的时刻拿着相机出门，因为雨后的世界总有一种被洗刷过的新鲜感。", "author": "李思琪", "avatar": "李", "avatar_bg": "linear-gradient(135deg,#34D399,#6EE7B7)", "read_time": "5 分钟", "likes": 96, "comments": 18, "bg": "linear-gradient(145deg,#0F766E,#14B8A6,#5EEAD4)"},
    {"id": 3, "date": "2026-07-05", "title": "胶片的味道", "mood": "怀旧", "mood_class": "mood-nostalgic", "tag": "器材心得", "excerpt": "第一次冲洗自己的胶卷，看到影像在显影液中慢慢浮现，那种等待和惊喜交织的感觉，是数码摄影里体验不到的。胶片的颗粒感不是缺陷，而是一种温暖的质感。", "author": "陈雨薇", "avatar": "陈", "avatar_bg": "linear-gradient(135deg,#F59E0B,#FCD34D)", "read_time": "6 分钟", "likes": 132, "comments": 24, "bg": "linear-gradient(150deg,#78350F,#B45309,#F59E0B,#FCD34D)"},
    {"id": 4, "date": "2026-06-28", "title": "光影实验笔记", "mood": "好奇", "mood_class": "mood-curious", "tag": "技术探索", "excerpt": "这周尝试了一些新的布光技巧，用黑色卡纸和锡纸自制了反光板和束光筒。效果出奇地好——有时候限制反而能激发更多创意，器材不够想象力来凑。", "author": "周思远", "avatar": "周", "avatar_bg": "linear-gradient(135deg,#78716C,#A8A29E)", "read_time": "4 分钟", "likes": 87, "comments": 15, "bg": "linear-gradient(140deg,#1C1917,#44403C,#78716C,#A8A29E)"},
    {"id": 5, "date": "2026-06-20", "title": "第一次拍星空", "mood": "敬畏", "mood_class": "mood-inspired", "tag": "拍摄日记", "excerpt": "带上新买的赤道仪，驱车两小时远离城市光污染。当眼睛适应黑暗后，银河慢慢显现——那种浩瀚让人说不出来话。30秒长曝光下的星空，比肉眼看到的还要震撼十倍。", "author": "林子涵", "avatar": "林", "avatar_bg": "linear-gradient(135deg,#7C3AED,#A78BFA)", "read_time": "7 分钟", "likes": 178, "comments": 42, "bg": "linear-gradient(155deg,#1E1B4B,#312E81,#4F46E5,#818CF8)"},
    {"id": 6, "date": "2026-06-14", "title": "街角咖啡馆", "mood": "热情", "mood_class": "mood-excited", "tag": "街拍日记", "excerpt": "街拍最有趣的地方在于，你永远不知道下一秒会遇见什么。这家咖啡馆的光线简直完美，透过落地窗洒进来的自然光让每一个角落都像一幅画。", "author": "赵一凡", "avatar": "赵", "avatar_bg": "linear-gradient(135deg,#EA580C,#FB923C)", "read_time": "3 分钟", "likes": 65, "comments": 9, "bg": "linear-gradient(148deg,#7C2D12,#C2410C,#FB923C,#FDBA74)"},
]

HISTORY_EVENTS = [
    {"year": "2018", "title": "凌镜摄影社团成立", "desc": "由一群热爱摄影的同学自发组织，从最初的 15 人发展至今。"},
    {"year": "2019", "title": "首届校园摄影展", "desc": "在学校图书馆举办首届摄影展，展出作品 80 余幅，参观人数超过 2000 人次。"},
    {"year": "2020", "title": "线上转型与疫情应对", "desc": "面对疫情挑战，社团迅速转型线上运营，开展线上讲座、云展览等创新活动。"},
    {"year": "2021", "title": "工作室正式开放", "desc": "学校批准社团使用一间办公室作为工作室，配备灯光、背景布等专业设备。"},
    {"year": "2023", "title": "校企合作项目", "desc": "与本地多家摄影工作室建立合作，为成员提供实习和作品展示机会。"},
    {"year": "2025", "title": "社团影响力扩大", "desc": "成员突破 200 人，年度活动 30+ 场，成为学校最具影响力的艺术社团之一。"},
]

RESOURCES = [
    {"id": 1, "cat": "tutorial", "title": "人像摄影入门完全指南", "desc": "从构图到用光，从器材选择到后期调色，系统学习人像摄影的核心技巧。涵盖室内外场景、自然光与人造光的使用方法，帮助你快速提升人像作品质量。", "tag": "摄影教程", "author": "张明远", "views": "3.2k", "downloads": "1.8k", "bg": "linear-gradient(135deg, #2D5F8A, #4A90D9, #6AADE8)"},
    {"id": 2, "cat": "post", "title": "Lightroom 调色 workflow 详解", "desc": "详解从 RAW 到成片的完整调色流程，包括曝光校正、白平衡调整、HSL 面板运用、预设创建等关键步骤，附带 10 组凌镜专属调色预设。", "tag": "后期技巧", "author": "李思琪", "views": "2.7k", "downloads": "1.5k", "bg": "linear-gradient(135deg, #6D28D9, #8B5CF6, #A78BFA)"},
    {"id": 3, "cat": "gear", "title": "2026 学生党相机选购指南", "desc": "针对预算有限的摄影爱好者，全面对比佳能、尼康、索尼三大品牌入门级机型的画质、对焦、视频能力与性价比，助你找到最适合的第一台相机。", "tag": "器材评测", "author": "王浩宇", "views": "4.1k", "downloads": "2.3k", "bg": "linear-gradient(135deg, #0369A1, #0EA5E9, #38BDF8)"},
    {"id": 4, "cat": "composition", "title": "构图法则：从三分法到视觉引导", "desc": "深入解析经典构图法则的原理与实战应用，涵盖三分法、黄金螺旋、对角线构图、框架构图等多种技巧，通过 50+ 实例帮助你掌握画面结构的艺术。", "tag": "构图指南", "author": "陈雨薇", "views": "2.9k", "downloads": "1.2k", "bg": "linear-gradient(135deg, #047857, #10B981, #34D399)"},
    {"id": 5, "cat": "light", "title": "自然光摄影：抓住黄金时刻", "desc": "详解日出日落、蓝色时刻、逆光与侧光等自然光条件下拍摄技巧。学会利用光线塑造画面氛围，让每一张照片都充满戏剧性与层次感。", "tag": "光影知识", "author": "林子涵", "views": "2.1k", "downloads": "980", "bg": "linear-gradient(135deg, #B45309, #F59E0B, #FBBF24)"},
    {"id": 6, "cat": "tutorial", "title": "街拍纪实：记录城市的脉搏", "desc": "从布列松的决定性瞬间到当代街头摄影实践，学习如何在街头捕捉生活瞬间。探讨快拍技巧、盲拍方法以及街拍中的法律与伦理问题。", "tag": "摄影教程", "author": "赵一凡", "views": "1.8k", "downloads": "860", "bg": "linear-gradient(135deg, #BE185D, #EC4899, #F472B6)"},
    {"id": 7, "cat": "post", "title": "Photoshop 人像精修技法", "desc": "零基础学习人像精修核心技法，包括磨皮、液化、色彩分级与背景处理。附带凌镜出片标准流程与练习素材包，可跟随教程逐步实操。", "tag": "后期技巧", "author": "李思琪", "views": "3.5k", "downloads": "2.1k", "bg": "linear-gradient(135deg, #4338CA, #6366F1, #818CF8)"},
    {"id": 8, "cat": "gear", "title": "镜头选择指南：定焦 vs 变焦", "desc": "深入分析不同焦段镜头的成像特点与适用场景，从 35mm 到 200mm 的全面对比。帮助你根据拍摄题材和个人预算，构建最实用的镜头配置方案。", "tag": "器材评测", "author": "王浩宇", "views": "2.4k", "downloads": "1.1k", "bg": "linear-gradient(135deg, #0F766E, #14B8A6, #2DD4BF)"},
    {"id": 9, "cat": "light", "title": "闪光灯入门与布光实战", "desc": "从机顶闪光灯到离机闪，从单灯到多灯布光方案。详解 TTL 与手动模式的区别、柔光箱选择、反射布光技巧，让闪光灯不再是你的短板。", "tag": "光影知识", "author": "林子涵", "views": "1.6k", "downloads": "750", "bg": "linear-gradient(135deg, #92400E, #D97706, #FCD34D)"},
]

STUDIO_EQUIPMENT = [
    {"name": "佳能 EOS R5", "type": "机身", "status": "可用"},
    {"name": "索尼 A7R IV", "type": "机身", "status": "可用"},
    {"name": "尼康 Z7 II", "type": "机身", "status": "借出"},
    {"name": "24-70mm f/2.8 镜头", "type": "镜头", "status": "可用"},
    {"name": "70-200mm f/2.8 镜头", "type": "镜头", "status": "可用"},
    {"name": "50mm f/1.8 镜头", "type": "镜头", "status": "可用"},
    {"name": "35mm f/1.4 镜头", "type": "镜头", "status": "借出"},
    {"name": "柔光箱套装", "type": "灯光", "status": "可用"},
    {"name": "LED 补光灯", "type": "灯光", "status": "可用"},
    {"name": "三脚架", "type": "配件", "status": "可用"},
    {"name": "背景布套装", "type": "背景", "status": "可用"},
    {"name": "稳定器", "type": "配件", "status": "借出"},
]
