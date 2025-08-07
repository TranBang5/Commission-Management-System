import re
import pymysql
from datetime import datetime
from typing import Dict, Tuple, Any

class DataNormalizer:
    def __init__(self, mysql_config: Dict[str, Any]):
        """
        Khởi tạo kết nối MySQL.
        mysql_config: dict chứa các thông tin kết nối (host, user, password, db, ...)
        """
        self.conn = pymysql.connect(**mysql_config)

    def validate_input(self, data: dict, data_type: str) -> Tuple[bool, list]:
        """
        Kiểm tra dữ liệu đầu vào theo từng loại (project, employee, client).
        Trả về (True, []) nếu hợp lệ, (False, [danh sách lỗi]) nếu không hợp lệ.
        """
        errors = []
        if data_type == 'project':
            # TODO: Kiểm tra các trường bắt buộc, định dạng ngày, số...
            pass
        elif data_type == 'employee':
            # TODO: Kiểm tra các trường bắt buộc, email, phone, ngày sinh...
            pass
        elif data_type == 'client':
            # TODO: Kiểm tra các trường bắt buộc, email, tax_code...
            pass
        else:
            errors.append('Unknown data_type')
        return len(errors) == 0, errors

    def normalize_data(self, data: dict, data_type: str) -> dict:
        """
        Chuẩn hoá dữ liệu đầu vào theo từng loại.
        Trả về dict đã chuẩn hoá.
        """
        norm = dict(data)
        if data_type == 'project':
            # TODO: Chuẩn hoá ngày tháng, số, status...
            pass
        elif data_type == 'employee':
            # TODO: Chuẩn hoá ngày sinh, email, phone, status...
            pass
        elif data_type == 'client':
            # TODO: Chuẩn hoá tax_code, email, phone...
            pass
        return norm

    def save_to_database(self, data: dict, data_type: str):
        """
        Lưu dữ liệu đã chuẩn hoá vào MySQL.
        """
        with self.conn.cursor() as cursor:
            if data_type == 'project':
                # TODO: Viết câu lệnh insert/update cho bảng projects
                pass
            elif data_type == 'employee':
                # TODO: Viết câu lệnh insert/update cho bảng employees
                pass
            elif data_type == 'client':
                # TODO: Viết câu lệnh insert/update cho bảng clients
                pass
            self.conn.commit()

    # Các hàm phụ trợ
    def _is_valid_date(self, date_str: str) -> bool:
        """Kiểm tra định dạng ngày hợp lệ (YYYY-MM-DD hoặc DD/MM/YYYY)"""
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
            try:
                datetime.strptime(date_str, fmt)
                return True
            except:
                continue
        return False

    def _normalize_date(self, date_str: str) -> str:
        """Chuyển đổi nhiều định dạng ngày về YYYY-MM-DD"""
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        return date_str

    def _normalize_email(self, email: str) -> str:
        """Chuẩn hoá email (lowercase, loại bỏ khoảng trắng)"""
        return email.strip().lower() if email else ''

    def _normalize_phone(self, phone: str) -> str:
        """Chuẩn hoá số điện thoại (chỉ giữ số)"""
        return re.sub(r'\D', '', phone) if phone else ''
