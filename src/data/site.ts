// Business facts used across the site. Items marked TODO are unconfirmed — check with the owner.

export const site = {
  name: 'Superior Land & Site Services',
  // TODO: confirm legal entity / DBA (Facebook page is "Superior Bobcat Services LLC.")
  legalName: 'Superior Land & Site Services',
  tagline: 'Site work, done right from the ground up.',
  description:
    'Commercial, municipal and large-acreage site work in West-Central Ohio: clearing, grading, ponds, drainage, access roads and final stabilization.',
  phone: '937-539-3002',
  phoneHref: 'tel:+19375393002',
  email: '', // TODO: owner email for bids
  // TODO: confirm. 937-539 is the Bellefontaine / Logan County exchange.
  region: 'West-Central Ohio',
  state: 'OH',
  serviceArea: [] as string[], // TODO: counties served
  hours: 'Mon–Fri, 7am–5pm', // TODO: confirm
  facebook: 'https://www.facebook.com/profile.php?id=100083360259884',
  /** Owner only takes residential work at this size and up */
  minResidentialAcres: 3,
} as const;

/** Who the business works for — drives home/about copy and the bid form. */
export const audiences = [
  {
    key: 'commercial',
    title: 'Contractors & Developers',
    text: 'Site prep, pads, stone and final grading for general contractors, developers, schools and industrial owners.',
  },
  {
    key: 'municipal',
    title: 'Municipalities & Townships',
    text: 'Right-of-way and roadside clearing, ditch and berm restoration, and culvert work for townships, villages and counties.',
  },
  {
    key: 'acreage',
    title: 'Estates & Acreage',
    text: `Clearing, ponds, access drives and grading for residential properties of ${site.minResidentialAcres}+ acres.`,
  },
] as const;

/** Equipment visible in job photos. TODO: confirm the full list with the owner. */
export const equipment = [
  'Peterbilt with gooseneck equipment trailer',
  'John Deere 60G excavator with mulching head',
  'Compact track loaders with forestry mulcher',
  'Straw blower for large-area stabilization',
] as const;

export const nav = [
  { label: 'Services', href: 'services/' },
  { label: 'Projects', href: 'projects/' },
  { label: 'Service Area', href: 'service-area/' },
  { label: 'About', href: 'about/' },
] as const;
