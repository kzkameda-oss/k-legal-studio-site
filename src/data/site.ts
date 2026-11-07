// 事務所の基本情報。サイト全体で参照する唯一の場所。
export const site = {
  name: '亀田行政書士事務所',
  nameEn: 'Kameda Legal Studio',
  domain: 'https://k-legal-studio.com',
  representative: '亀田 和正',
  representativeTitle: '行政書士',
  registrationNo: '第10260611号',
  association: '奈良県行政書士会',
  postal: '〒631-0824',
  address: '奈良県奈良市西大寺南町16番19号',
  tel: '0742-53-1560',
  telHref: 'tel:0742531560',
  fax: '0742-53-1529',
  mobile: '070-1835-1560',
  mobileHref: 'tel:07018351560',
  email: 'kz.kameda@k-legal-studio.com',
  hours: '平日 9:00〜17:00（土日祝は事前予約制）',  // 2026-11-08 オーナー確認済
  access: '近鉄「大和西大寺」駅南口より徒歩約5分（駐車場あり）',  // 2026-11-08 オーナー確認済
  area: '奈良県全域・京都府南部・大阪府（その他の地域もご相談ください）',  // 2026-11-08 オーナー確認済
  // お問い合わせフォームの送信先（Formspree等のURL）。空ならフォームは表示せず電話・メール案内のみ。
  formEndpoint: '',
  description:
    '奈良市西大寺の行政書士事務所。建設業許可・経営事項審査・農地転用・産業廃棄物収集運搬業許可・宅建業免許など、許認可申請を専門に対応しています。',
};

export const nav = [
  { href: '/services/', label: '業務案内' },
  { href: '/flow/', label: 'ご依頼の流れ' },
  { href: '/price/', label: '料金について' },
  { href: '/about/', label: '事務所案内' },
  { href: '/contact/', label: 'お問い合わせ' },
];
