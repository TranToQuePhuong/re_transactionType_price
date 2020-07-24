# Patterns for unit price
# References: https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
# Final pattern: pr_ptrn
# Sub patterns: val_pattern, cur_u, time_u
pr_ptrn = r'[.]?[\d]+(?:,\d+)*(?:\.\d+)*\s*(đồng|dong|tr(iệ|ie)u\s*\d*|tr\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ)?\s*(\/\s*1?\s*th([áa]ng)?|\/\s*m\s*2\s*\/\s*1?\s*th([áa]ng)?)'
pr_approximate = r'(dự kiến|khoảng|tầm|hơn)'
numbers = r'(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'
val_ptrn = r'(giá)?\s*(cho thuê|thuê)?\s*:?\s*{}?\s*[.]?(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'.format(
    pr_approximate)
cur_u_r = r'\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ|đ)?'
cur_u_man_r = r'\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ|đ)'
time_u = r'\s*(\/\s*1?\s*th([áa]ng)?(\s*\/\s*m\s*2)?|\/\s*\d*\s*m\s*2(\s*\/\s*1?\s*th([áa]ng)?)?|\/\s*1\s*năm|\/\s*năm)'
time_u_2 = r'\s*(\/\s*1?\s*th([áa]ng)?|\/\s*\d*\s*m\s*2\s*\/\s*1?\s*th([áa]ng)?|\/\s*1\s*năm|\/\s*năm)'
u_pr_floor = r'\d\s*tr(ệt|et)?(,\s*|\s+)\d\s*l(ầu|au)'
################################################################################


################################################################################
# Check kw, text should be of one these pattern
r_valid = r'(\/\s*1?\s*th[áa]ng|phòng .*riêng|\/\s*ph[òo]ng|\/\s*th|\/\s*month|rent|cọc\s*[12]\s*(tháng|th)|thu[êe])'
################################################################################


################################################################################
# Check kw, text cannot be any of these
r_nin_1 = r'(bán |san(g)? nhượng|nhượng)\s*(gấp)?\s*(nhà|chung cư|căn hộ|đất|biệt thự)?\s*(và|hoặc|\/)?\s*(cho thuê|thuê)?'
r_nin_2 = r'{}.*đang cho\s*(khách|người)?\s*(nước ngoài)?\s*thuê'.format(r_nin_1)
r_nin_3 = r'{}.*hợp đồng (cho)?\s*thuê'.format(r_nin_1)
r_nin_4 = r'{}.*\d\/\s*thanh'.format(r_nin_1)
r_nin_5 = r'{}.*doanh thu (dự kiến|khoảng)'.format(r_nin_1)
r_nin_6 = r'(sổ (đỏ|hồng)?|sổ (đỏ|hồng)?\s*riêng)'
# r_msg_invalid = r'^(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*).*$'.format(
#     r_nin_1, r_nin_2, r_nin_3, r_nin_4, r_nin_5)
# r_title_invalid = r'^((?!{}).)*$'.format(r_nin_1)
################################################################################


################################################################################
# Pattern for land, warehouse
land_wh = r'((nền)?\s*đất\s*(nền)?|(nhà)?\s*kho(\s+|\.)|x(ưở|uo)ng)'
# Contract
contract = r'(đang cho\s*(khách|người)?\s*(nước ngoài)?\s*thuê|hợp đồng (cho)?\s*thuê)'
################################################################################


################################################################################
# Pattern for sell
val_ptrn_s = r'(giá)?\s*(bán)?\s*:?\s*{}?\s*[.]?(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'.format(
    pr_approximate)
val_ptrn_rs = r'(giá)?\s*(bán|cho thuê|thuê)?\s*:?\s*{}?\s*[.]?(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'.format(
    pr_approximate)

# Works fine but some cases is wrong
# Because 'tr(iệ|ie)u\s*\d*\/tháng', 'tr\s*\d*\/tháng' is not sell
# /tr\s*\d*/i : vẫn bắt từ khóa 'trệt'
# /tr(?!( [1-9]lầu|ệt))\s*\d*/i : không bắt những pattern dạng 'tr 1 lầu', 'tr 1l'
cur_u_s = r'\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr(?!( ?,?\s*[1-9]\s*l([ầa]u)?|ệt|\s*\/))\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ)?'
cur_u_man_s = r'\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr(?!( ?,?\s*[1-9]\s*l([ầa]u)?|ệt|\s*\/))\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ)'

# stuck when records more than 200,000
# cur_u_s = r'\s*(đồng|dong|tr(iệ|ie)u\s*\d*\s|tr\s*\d*\s|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ)?'
# cur_u_man_s = r'\s*(đồng|dong|tr(iệ|ie)u\s*\d*\s|tr\s*\d*\s|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ)'

u_pr_s = r'\s*\/\s*m\s*2'
u_pr_s_area = r'\s*(\/\s*\d+\s*m\s*2|\/\s*m\s*2)'

# Check keyword
s_in_1 = r'bán (gấp)?.{0,10}\s*(nhà|chung cư|căn hộ|đất|biệt thự)?\s*(và|hoặc|\/)?\s*(cho thuê|thuê)?'
s_in_2 = r'(sổ (đỏ|hồng)?|sổ (đỏ|hồng)?\s*riêng)'
s_nin_2 = r'{}'.format(r_valid)

# s_renting_with_pr_ptrn = r'{}(.{1}){}{}({})?'.format(contract, val_ptrn, cur_u_r, time_u)
s_renting_with_pr_ptrn = r'(đang cho thuê|hợp đồng (cho)?\s*thuê)(.{1,40})((giá)?\s*(bán)?\s*:?\s*(dự kiến|khoảng|tầm|hơn)?\s*[.]?(\d+)\s*(,\s*\d+)*(\.\s*\d+)*)?\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr(?!( ?,?\s*[1-9]\s*l([ầa]u)?|ệt|\s*\/))\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ|đ)?\s*(\/\s*1?\s*th([áa]ng)?(\s*\/\s*m\s*2)?|\/\s*\d*\s*m\s*2\s*\/\s*1?\s*th([áa]ng)?|\/\s*1\s*năm|\/\s*năm)?'
s_renting_with_pr_ptrn_1 = r'(đang cho thuê|hợp đồng (cho)?\s*thuê)(giá)?\s*(bán)?\s*:?\s*(dự kiến|khoảng|tầm|hơn)?\s*[.]?(\d+)\s*(,\s*\d+)*(\.\s*\d+)*\s*(đồng|dong|triệu\s*\d*|trieu\s*\d*|tr(?!( ?,?\s*[1-9]\s*l([ầa]u)?|ệt|\s*\/))\s*\d*|t[ỉiỷy]\s*\d*|USD|\$\s*(USD)?|ngàn|VND|VNĐ|đ)?\s*(\/\s*1?\s*th([áa]ng)?(\s*\/\s*m\s*2)?|\/\s*\d*\s*m\s*2\s*\/\s*1?\s*th([áa]ng)?|\/\s*1\s*năm|\/\s*năm)?'
s_renting_with_pr_ptrn_2 = r'thu nhập ((mỗi|một|1|hàng)\s*tháng {}{}{}?|(tháng)?\s*{}{}{}?)'\
    .format(val_ptrn, cur_u_r, time_u, val_ptrn, cur_u_r, time_u)
# s_renting_with_pr_ptrn_3 = r'((giá)?{}(cho thuê|thuê)|doanh thu)\s*((mỗi|một|1|hàng)?\s*tháng)?\s*{}?\s*{}{}{}?'\
#     .format(r'.{0,30}', pr_approximate, val_ptrn, cur_u_r, time_u)
s_renting_with_pr_ptrn_3 = r'((giá)?\s*(cho thuê|thuê)|doanh thu)\s*((mỗi|một|1|hàng)?\s*tháng)?\s*{}?\s*{}{}{}?'\
    .format(pr_approximate, val_ptrn, cur_u_r, time_u)

# Business potential
b_p_kw = r'((thuận)?\s*tiện\s*(lợi)?|lợi|(phù|thích) hợp|dễ|có (thể|khả năng)|khả năng)'
business = r'(ngân hàng|nhà hàng|tiệm|quán|cửa hàng|văn phòng|vp|công t[iy])'
services = r'((cho)?\s*thuê|kinh doanh|kd|(buôn|mua) bán|đầu tư|(mở|làm))\s*{}?'.format(business)
s_business_potential = r'{}{}{}([\.,\s]|{})'\
    .format(b_p_kw, r'.{1,40}', services, b_p_kw)
################################################################################


################################################################################
# Pattern for sang nhượng
transfer_ptrn = r'(san(g)? nhượng|nhượng)'
################################################################################


################################################################################
# Pattern for posts both sell and rent
s_and_r_ptrn = r'^(do)?.{0,50}(chính chủ)?\s*(cần)?\s*bán hoặc (cho)?\s*thuê'


################################################################################
# Check kw for sell posts
s_valid = r'^(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*)(?=.*((?!{}).)*).*$'\
    .format(r'thu[êe]', r'\/\s*1?\s*th[áa]ng', r'phòng .*riêng', r'\/\s*ph[òo]ng', r'\/\s*th', r'\/\s*month', r'rent', r'cọc\s*[12]\s*(tháng | th)')
################################################################################


################################################################################
# USD/VND ratio
usd_2_vnd = 23000
################################################################################


################################################################################
# Rent range
rent_range = [299999, 500000000]
################################################################################


################################################################################
# save_to_files.py
result_dir = './results/'
s_fn = 'sell.csv'
s_d_fn = 'sell_debug.txt'
r_fn = 'rent.csv'
r_d_fn = 'rent_debug.txt'
s_renting_with_pr = 'sell_renting_with_pr.csv'
# s_renting_with_pr_debug = 'sell_renting_with_pr_debug.txt'
s_renting_without_pr = 'sell_renting_without_pr.csv'
# s_renting_without_pr_debug = 'sell_renting_without_pr_debug.txt'
s_business_potential_file = 'sell_with_business_potential.csv'
sell_rent = 'both_sell_and_rent.csv'
sell_rent_debug = 'both_sell_and_rent_debug.txt'
final = 'all_results.txt'
# Test
test_dir = result_dir + 'test/'
test_r = 'test_rent.csv'
test_s = 'test_sell.csv'
test_s_r_w_pr = 'test_sell_renting_with_price.csv'
test_s_r_wo_pr = 'test_sell_renting_without_price.csv'
test_s_w_b_p = 'test_sell_w_business_potential.csv'
test_r_debug = 'test_rent_debug.txt'
test_s_debug = 'test_sell_debug.txt'
################################################################################


################################################################################
# Mongo shell
# Exlude trash (Get by running script)
# id_list = []
# db.posts.find().forEach(function(d){ var count = 0; for (f in d) {count++;} if (count < 35) {id_list.push(d._id);}});
################################################################################
