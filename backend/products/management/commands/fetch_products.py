"""
금융감독원 금융상품통합비교공시 API에서 예금/적금 데이터를 가져와 DB에 저장하는 커맨드
사용법: python manage.py fetch_products
중복 방지: fin_prdt_cd(금융상품코드)를 기준으로 update_or_create 처리
"""
# pylint: disable=no-member

import os
import requests
from django.core.management.base import BaseCommand
from products.models import FinancialProduct, ProductOption


# FSS API 기본 설정
FSS_BASE_URL = 'https://finlife.fss.or.kr/finlifeapi'
FSS_API_KEY = os.environ.get('FSS_API_KEY')

# 조회할 금융회사 그룹 코드
# 020000: 은행, 030200: 저축은행, 030300: 신협, 050000: 보험
TOP_FIN_GRP_CODES = ['020000', '030300']  # 은행, 저축은행


class Command(BaseCommand):  # pylint: disable=no-member
    """금융감독원 API에서 예금/적금 상품 데이터를 가져와 DB에 저장하는 커맨드"""

    help = '금융감독원 API에서 예금/적금 상품 데이터를 가져와 DB에 저장합니다.'

    def handle(self, *args, **options):
        if not FSS_API_KEY:
            self.stderr.write(self.style.ERROR('FSS_API_KEY 환경변수가 설정되지 않았습니다.'))
            return

        self.stdout.write('📦 금융상품 데이터 수집 시작...\n')

        total_created = 0
        total_updated = 0

        for grp_code in TOP_FIN_GRP_CODES:
            self.stdout.write(f'  [그룹코드: {grp_code}] 예금 조회 중...')
            created, updated = self._fetch_and_save(grp_code, product_type='D')
            total_created += created
            total_updated += updated

            self.stdout.write(f'  [그룹코드: {grp_code}] 적금 조회 중...')
            created, updated = self._fetch_and_save(grp_code, product_type='S')
            total_created += created
            total_updated += updated

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ 완료! 신규 저장: {total_created}건 / 업데이트: {total_updated}건'
            )
        )

    def _fetch_and_save(self, top_fin_grp_no, product_type):
        """API 호출 후 상품 및 옵션을 DB에 저장. (신규, 업데이트) 건수 반환"""
        url, type_label = self._get_api_url(product_type)
        created_count = 0
        updated_count = 0
        page = 1

        while True:
            data = self._call_api(url, top_fin_grp_no, page)
            if data is None:
                break

            result = data.get('result', {})
            base_list = result.get('baseList', [])
            option_list = result.get('optionList', [])

            if not base_list:
                break

            # optionList를 fin_prdt_cd 기준 그룹핑
            options_map = {}
            for opt in option_list:
                code = opt.get('fin_prdt_cd')
                options_map.setdefault(code, []).append(opt)

            for item in base_list:
                created, updated = self._save_product(item, options_map, product_type)
                created_count += created
                updated_count += updated

            # 다음 페이지 없으면 종료
            total_count = result.get('totalCount', 0)
            if page * 20 >= total_count:
                break
            page += 1

        self.stdout.write(f'    → {type_label} 신규 {created_count}건 / 업데이트 {updated_count}건')
        return created_count, updated_count

    def _call_api(self, url, top_fin_grp_no, page, retries=3):
        """FSS API 호출. 실패 시 최대 retries회 재시도 후 None 반환"""
        params = {
            'auth': FSS_API_KEY,
            'topFinGrpNo': top_fin_grp_no,
            'pageNo': page,
        }
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                self.stderr.write(self.style.WARNING(f'    API 호출 실패 ({attempt}/{retries}): {e}'))
        return None

    def _build_product_data(self, item, product_type):
        """API 응답 item을 DB 저장용 dict로 변환 (FSS API baseinfo 필드 기준)"""
        return {
            'fin_co_no': item.get('fin_co_no', ''),
            'kor_co_nm': item.get('kor_co_nm', ''),
            'fin_prdt_nm': item.get('fin_prdt_nm', ''),
            'product_type': product_type,
            'join_way': item.get('join_way', ''),
            'join_member': item.get('join_member', ''),
            'join_deny': item.get('join_deny', ''),
            'spcl_cnd': item.get('spcl_cnd', ''),
            'etc_note': item.get('etc_note', ''),
            'mtrt_int': item.get('mtrt_int', ''),
            'max_limit': item.get('max_limit'),
            'dcls_month': item.get('dcls_month', ''),
            'dcls_strt_day': item.get('dcls_strt_day', ''),
            'dcls_end_day': item.get('dcls_end_day'),
            'fin_co_subm_day': item.get('fin_co_subm_day', ''),
        }

    def _save_product(self, item, options_map, product_type):
        """
        단일 상품을 DB에 저장 (update_or_create)
        fin_prdt_cd 기준으로 중복 체크 → 신규면 create, 있으면 update
        반환: (created_count, updated_count)
        """
        fin_prdt_cd = item.get('fin_prdt_cd')

        product, created = FinancialProduct.objects.update_or_create(
            fin_prdt_cd=fin_prdt_cd,
            defaults=self._build_product_data(item, product_type),
        )

        for opt in options_map.get(fin_prdt_cd, []):
            self._save_option(product, opt)

        return (1, 0) if created else (0, 1)

    def _save_option(self, product, opt):
        """금리 옵션을 DB에 저장 (update_or_create)"""
        ProductOption.objects.update_or_create(
            product=product,
            intr_rate_type=opt.get('intr_rate_type', ''),
            rsrv_type=opt.get('rsrv_type', ''),
            save_trm=opt.get('save_trm', 0),
            defaults={
                'intr_rate_type_nm': opt.get('intr_rate_type_nm', ''),
                'rsrv_type_nm': opt.get('rsrv_type_nm', ''),
                'intr_rate': opt.get('intr_rate'),
                'intr_rate2': opt.get('intr_rate2'),
            },
        )

    def _get_api_url(self, product_type):
        """상품 유형에 따라 API URL과 라벨 반환"""
        if product_type == 'D':
            return f'{FSS_BASE_URL}/depositProductsSearch.json', '정기예금'
        return f'{FSS_BASE_URL}/savingProductsSearch.json', '정기적금'
