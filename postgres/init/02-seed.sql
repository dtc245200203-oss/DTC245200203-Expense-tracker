-- Seed Initial Categories & Realistic Transactions

INSERT INTO categories (id, name, type, icon, color) VALUES
-- Chi tiêu (Expense)
(1, 'Ăn uống & Cà phê', 'expense', 'utensils', '#ef4444'),
(2, 'Nhà ở & Tiền điện nước', 'expense', 'house', '#f97316'),
(3, 'Đi lại & Xăng xe', 'expense', 'car', '#eab308'),
(4, 'Mua sắm & Đồ dùng', 'expense', 'bag-shopping', '#8b5cf6'),
(5, 'Giải trí & Phim ảnh', 'expense', 'film', '#ec4899'),
(6, 'Y tế & Sức khỏe', 'expense', 'heart-pulse', '#06b6d4'),
(7, 'Giáo dục & Sách vở', 'expense', 'graduation-cap', '#3b82f6'),
-- Thu nhập (Income)
(8, 'Lương chính', 'income', 'money-bill-wave', '#10b981'),
(9, 'Thưởng & Làm thêm', 'income', 'gift', '#14b8a6'),
(10, 'Đầu tư & Cổ tức', 'income', 'chart-line', '#6366f1')
ON CONFLICT (id) DO NOTHING;

-- Reset sequence to maximum category id
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));

-- Seed Transactions across recent months
INSERT INTO transactions (amount, type, category_id, transaction_date, description) VALUES
-- Tháng gần nhất
(25000000.00, 'income', 8, CURRENT_DATE - INTERVAL '15 days', 'Nhận lương tháng chuyển khoản ngân hàng'),
(3500000.00, 'income', 9, CURRENT_DATE - INTERVAL '10 days', 'Thưởng dự án hoàn thành xuất sắc'),
(5500000.00, 'expense', 2, CURRENT_DATE - INTERVAL '14 days', 'Thanh toán tiền thuê nhà và internet'),
(650000.00, 'expense', 1, CURRENT_DATE - INTERVAL '12 days', 'Đi siêu thị mua thực phẩm tuần'),
(250000.00, 'expense', 3, CURRENT_DATE - INTERVAL '11 days', 'Đổ xăng xe máy và gửi xe'),
(1200000.00, 'expense', 4, CURRENT_DATE - INTERVAL '8 days', 'Mua sắm quần áo và giày thể thao'),
(350000.00, 'expense', 1, CURRENT_DATE - INTERVAL '6 days', 'Ăn tối liên hoan cùng bạn bè'),
(450000.00, 'expense', 5, CURRENT_DATE - INTERVAL '4 days', 'Xem phim rạp và cà phê cuối tuần'),
(800000.00, 'expense', 7, CURRENT_DATE - INTERVAL '2 days', 'Mua giáo trình và khóa học trực tuyến'),
(150000.00, 'expense', 1, CURRENT_DATE - INTERVAL '1 day', 'Cà phê sáng làm việc'),

-- Tháng trước
(25000000.00, 'income', 8, CURRENT_DATE - INTERVAL '45 days', 'Nhận lương tháng trước'),
(2000000.00, 'income', 10, CURRENT_DATE - INTERVAL '40 days', 'Lãi suất tiết kiệm và cổ tức'),
(5500000.00, 'expense', 2, CURRENT_DATE - INTERVAL '44 days', 'Tiền thuê căn hộ tháng trước'),
(1800000.00, 'expense', 1, CURRENT_DATE - INTERVAL '42 days', 'Tiền ăn uống sinh hoạt gia đình'),
(750000.00, 'expense', 4, CURRENT_DATE - INTERVAL '38 days', 'Mua đồ gia dụng phòng bếp'),
(300000.00, 'expense', 3, CURRENT_DATE - INTERVAL '35 days', 'Bảo dưỡng xe máy định kỳ'),

-- 2 tháng trước
(24000000.00, 'income', 8, CURRENT_DATE - INTERVAL '75 days', 'Nhận lương tháng trước nữa'),
(5500000.00, 'expense', 2, CURRENT_DATE - INTERVAL '74 days', 'Tiền thuê nhà'),
(2200000.00, 'expense', 1, CURRENT_DATE - INTERVAL '70 days', 'Thực phẩm và ăn uống'),
(1500000.00, 'expense', 6, CURRENT_DATE - INTERVAL '65 days', 'Khám sức khỏe tổng quát và thuốc')
ON CONFLICT DO NOTHING;
