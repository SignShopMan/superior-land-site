// Business facts used across the site. Items marked TODO are unconfirmed — check with the owner.

export const site = {
  name: 'Superior Land & Site Services',
  // TODO: confirm legal entity / DBA (Facebook page is "Superior Bobcat Services LLC.")
  legalName: 'Superior Land & Site Services',
  tagline: 'Built for tough ground.',
  description:
    'Gravel driveways, land clearing, forestry mulching, grading & seeding, ponds, drainage and site prep. Free quotes. Call 937-539-3002.',
  phone: '937-539-3002',
  phoneHref: 'tel:+19375393002',
  email: '', // TODO: owner email for quotes
  // TODO: confirm service area; 937 = Dayton / Miami Valley / west-central Ohio
  region: 'Western Ohio',
  state: 'OH',
  serviceArea: [] as string[], // TODO: list of towns/counties
  hours: 'Mon–Sat, 7am–7pm', // TODO: confirm
  facebook: 'https://www.facebook.com/profile.php?id=100083360259884',
  // TODO: confirm each claim before launch
  trust: ['Free estimates', 'Owner on every job', 'Our own equipment'],
} as const;

export const nav = [
  { label: 'Services', href: 'services/' },
  { label: 'Projects', href: 'projects/' },
  { label: 'Service Area', href: 'service-area/' },
  { label: 'About', href: 'about/' },
  { label: 'Contact', href: 'contact/' },
] as const;
