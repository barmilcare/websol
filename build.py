from pathlib import Path
import re,html,json,shutil,hashlib,urllib.request
ROOT=Path(__file__).parent
OUT=ROOT/'dist'
source=(ROOT/'content.md').read_text()
def inline(s):
 s=html.escape(s)
 s=re.sub(r'\*\*(.*?)\*\*',r'<strong>\1</strong>',s)
 s=re.sub(r'\[([^\]]+)\]\(((?:/(?!/)|https://|mailto:)[^\s)]+)\)',r'<a href="\2">\1</a>',s)
 return s
pages=[]
for b in re.split(r'(?=^### (?:Page \d|Guide \d))',source,flags=re.M)[1:]:
 if not b.startswith(('### Page','### Guide')):continue
 b=re.split(r'^## [5678]\.',b,flags=re.M)[0]
 url=re.search(r'\*\*URL:\*\* `([^`]+)`',b)
 title=re.search(r'\*\*Title:\*\* (.+)',b)
 meta=re.search(r'\*\*Meta description:\*\* (.+)',b)
 body=re.search(r'^# (.+)',b,re.M)
 if not all([url,title,meta,body]):continue
 content=b[body.start():]
 content=re.split(r'^\*\*(?:Internal links|Editorial basis|Implementation note):',content,flags=re.M)[0]
 pages.append(dict(url=url[1],title=title[1].strip(),meta=meta[1].strip(),heading=body[1],content=content))
seo_plan=json.loads((ROOT/'seo-pages.json').read_text())
for page in pages:
 config=seo_plan['pages'].get(page['url'],{})
 for key in ('title','meta','heading'):
  if key in config:page[key]=config[key]
 if 'body' in config:page['content']='# '+page['heading']+'\n\n'+config['body']
 if 'append' in config:page['content']+='\n\n'+config['append']
 page['keywords']=config
privacy_content=(ROOT/'privacy.md').read_text()
pages.append(dict(url='/privacy/',title='Privacy | Web Solution Sydney',meta='How Web Solution Sydney handles website enquiries, email correspondence and technical website information.',heading='Privacy and your enquiry',content=privacy_content,keywords={}))

# Public project references retained from the existing business site. These are
# presented as linked examples, not as invented case-study outcomes.
portfolio_projects=[
 ('01','TFP Tax','Bookkeeping','https://www.tfptax.com.au/'),
 ('02','Rebuild Group','Construction / renovation','https://www.rebuildgroup.com.au/'),
 ('03','Whinbury Hill Equestrian','Horse riding','https://whinburyhillequestrian.com.au/'),
 ('04','Local Electrician','Electrical','https://www.localelectrician.com.au/'),
 ('05','Dingo','Skip bin / excavation','https://www.dingo.com.au/'),
 ('06','Citrus Clean','Carpet cleaning','https://citrusclean.com.au/'),
 ('07','Shore Clean','Cleaning','https://shoreclean.net.au/'),
 ('08','Park Beach Plaza','E-commerce','https://parkbeachplaza.com.au/'),
 ('09','Total Colour Painting','Painting','https://totalcolourpainting.com.au/'),
 ('10','Ju Flooring','Flooring','https://juflooring.com.au/'),
 ('11','All Shutters & Blinds','Blinds / shutters','https://allshuttersandblinds.com.au/'),
 ('12','Wynstan','Blinds / awnings','https://www.wynstan.com.au/'),
 ('13','Carnivalland','Amusement / entertainment','https://carnivalland.com.au/'),
 ('14','Reminisce Photography','Photography','https://reminiscephotography.com.au/'),
 ('15','Pool Care','Pool care','https://poolcarecompany.com.au/'),
 ('16','Epic Supply','E-commerce','https://epicsupply.com.au/'),
 ('17','Iconic Renovations','Renovation','https://iconicrenovationsco.com.au/'),
 ('18','GT Kitchen & Bathroom','Renovation','https://www.gtkitchenandbathroom.com.au/'),
 ('19','Call The Electrician','Electrical','https://www.calltheelectrician.com.au/'),
 ('20','SMS Mining','Industrial','https://smsmining.com.au/')
]

# Exact 800x600 screenshot sources verified on the existing business homepage.
# Each source belongs to one project; never substitute an unrelated photograph.
project_images={
 0:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fwww.tfptax.com.au%2F?w=800&h=600',
 1:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fwww.rebuildgroup.com.au%2F?w=800&h=600',
 2:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fwhinburyhillequestrian.com.au%2F?w=800&h=600',
 3:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fwww.localelectrician.com.au%2F?w=800&h=600',
 4:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fwww.dingo.com.au%2F?w=800&h=600',
 5:'https://s.wordpress.com/mshots/v1/https%3A%2F%2Fcitrusclean.com.au%2F?w=800&h=600',
}
def project_preview(index,url=None):
 source=project_images.get(index)
 if source is None and url:
  source='https://s.wordpress.com/mshots/v1/'+__import__('urllib.parse').parse.quote(url,safe='')+'?w=800&h=600'
 return html.escape(source,quote=True) if source else None
catalogue_categories=[
 ('01','AI-powered sites','Chatbots, smart forms and practical website workflows.'),
 ('02','E-commerce & catalogues','Shopping journeys, product catalogues and online stores.'),
 ('03','Dynamic sites','Custom-coded sites with content that can grow.'),
 ('04','Painting','Websites for painters, decorators and finishing teams.'),
 ('05','Amusement, games & entertainment','Party hire, amusements and event businesses.'),
 ('06','Photography','Portfolio-led websites for photographers and media studios.'),
 ('07','Furniture & interiors','Furniture, wardrobes and interior-focused businesses.'),
 ('08','Cleaning & pest control','Cleaning, carpet care and pest-control services.'),
 ('09','Renovation & construction trades','Renovation, patios, tiling, scaffolding and concreting.'),
 ('10','Excavation & demolition','Earthmoving, skip bins, demolition and rubbish removal.'),
 ('11','Building & architecture','Builders, architects and property-related services.'),
 ('12','Flooring','Flooring installers and specialist surface businesses.'),
 ('13','Welding & metal fabrication','Fabrication, welding and industrial workshop services.'),
 ('14','Specialty trades','Focused trade services that need a clear online presence.'),
 ('15','Electrical','Electrical contractors and service businesses.'),
 ('16','Lifestyle & services','Customer-focused local services and lifestyle brands.'),
 ('17','Landscaping','Garden design, landscaping and ongoing outdoor care.')
]
pages.extend([
 dict(url='/portfolio/',title='Portfolio | Web Solution Sydney',meta='Explore selected website projects across trades, services, retail and professional businesses.',heading='Selected work from across Australian businesses.',content='',keywords={'related':['/designs/','/contact/']}),
 dict(url='/designs/',title='Website Design Catalogue | Web Solution Sydney',meta='Browse the Web Solution Sydney design catalogue by industry, from AI-powered sites and e-commerce to trades and local services.',heading='A broader catalogue of website directions.',content='',keywords={'related':['/portfolio/','/website-packages/','/contact/']}),
])
page_by_url={p['url']:p for p in pages}
website_pages=[
 ('Website packages','/website-packages/'),
 ('Website redesign','/website-redesign/'),
 ('Small business web design','/small-business-web-design/'),
 ('Tradie websites','/tradie-websites/'),
 ('Electrician websites','/electrician-website-design/'),
 ('Plumber websites','/plumber-website-design/'),
 ('Cleaning business websites','/cleaning-website-design/'),
 ('Landscaping websites','/landscaping-website-design/')
]
growth_pages=[('Hosting & care','/website-hosting/'),('SEO services','/seo-services/'),('AI marketing','/ai-marketing/')]
guide_pages=[('About Web Solution Sydney','/about/'),('Website costs guide','/guides/website-costs/'),('Getting more enquiries guide','/guides/website-not-getting-enquiries/'),('Contact','/contact/')]
work_pages=[('Selected work','/portfolio/'),('Design catalogue','/designs/')]
brand='<a class="brand" href="/" aria-label="Web Solution Sydney home"><img src="/assets/logo.png" alt="Web Solution Sydney" width="190" height="102"></a>'
arrow='<span aria-hidden="true">↗</span>'
def nav_anchor(label,path,current):
 return f'<a{" aria-current=page" if current==path else ""} href="{path}">{label}</a>'
def nav_dropdown(label,items,current):
 active=' nav-active' if any(current==path for _,path in items) else ''
 return '<details class="nav-dropdown'+active+'"><summary>'+label+' <span aria-hidden="true">⌄</span></summary><div class="nav-menu">'+''.join(nav_anchor(n,p,current) for n,p in items)+'</div></details>'
def header(url):
 links=nav_dropdown('Websites',website_pages,url)+nav_dropdown('Growth',growth_pages,url)+nav_dropdown('Work',work_pages,url)+nav_dropdown('Guides',guide_pages,url)
 return '<header><div class="header-inner">'+brand+'<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu <span>☰</span></button><nav id="navigation">'+links+'<a class="button small" href="/contact/">Let’s talk '+arrow+'</a></nav></div></header>'
def footer():return '<footer><div class="footer-cta"><div><span class="eyebrow">LET’S BUILD SOMETHING USEFUL</span><h2>A website with<br><em>more momentum.</em></h2></div><a class="button" href="/contact/">Start a conversation '+arrow+'</a></div><div class="footer-top">'+brand+'<p>Web design, SEO and practical AI marketing for businesses ready to move forward.</p><div class="footer-contact"><span>QUICK CONTACT</span><a href="tel:+61420102599">0420 102 599 ↗</a><a href="mailto:ryan@websolutionsydney.com.au">ryan@websolutionsydney.com.au ↗</a></div></div><div class="footer-links"><div><span>WEBSITES</span>'+''.join('<a href="'+p+'">'+n+' <b>↗</b></a>' for n,p in website_pages[:4])+'</div><div><span>INDUSTRIES</span>'+''.join('<a href="'+p+'">'+n+' <b>↗</b></a>' for n,p in website_pages[4:])+'</div><div><span>GROW & MAINTAIN</span>'+''.join('<a href="'+p+'">'+n+' <b>↗</b></a>' for n,p in growth_pages)+'</div><div><span>EXPLORE & CONTACT</span>'+''.join('<a href="'+p+'">'+n+' <b>↗</b></a>' for n,p in work_pages+guide_pages)+'</div></div><div class="footer-bottom"><span>© 2026 Web Solution Sydney. Established 2017.</span><span>Serving Australian businesses remotely · Sydney / Australia</span></div></footer>'
services=[('01','Websites that mean business.','New websites and thoughtful redesigns. Clear content, considered design and a simple path to an enquiry.','Explore websites','/website-packages/','⌘'),('02','A little care goes a long way.','Keep your website running with hosting, maintenance and an agreed level of ongoing support.','Hosting & care','/website-hosting/','◈'),('03','Make your business easier to find.','Search strategy, useful content and technical improvements focused on the customers you want to reach.','Explore SEO','/seo-services/','◎'),('04','Put AI to practical use.','Website chatbots, enquiry workflows and content support. Start with one useful task.','Explore AI marketing','/ai-marketing/','✳')]
industries=[
 ('Small business','Small business web design','A clear starting point for a growing business.','/small-business-web-design/','01'),
 ('Electricians','Electrician website design','Make your services and quote process easier to understand.','/electrician-website-design/','02'),
 ('Plumbers','Plumber website design','Present your plumbing services clearly on every screen.','/plumber-website-design/','03'),
 ('Cleaning teams','Cleaning business websites','Build trust with focused service pages and simple enquiries.','/cleaning-website-design/','04'),
 ('Landscapers','Landscaping website design','Show your work and help local customers take the next step.','/landscaping-website-design/','05')
]
def industry_strip():
 return '<section class="industry-section section" id="industries"><div class="section-heading"><div><span class="eyebrow">INDUSTRY PAGES</span><h2>Built for the way<br><em>your business works.</em></h2></div><p>Start with a relevant page for your industry, then shape the rest of the website around your services, customers and goals.</p></div><div class="industry-grid">'+''.join('<a class="industry-card" href="'+path+'"><span>'+num+' /</span><h3>'+title+'</h3><p>'+desc+'</p><b>Explore page ↗</b></a>' for title,heading,desc,path,num in industries)+'</div></section>'
def selected_work():
 cards=''.join(
  '<a class="selected-project" href="'+url+'" target="_blank" rel="noopener noreferrer" aria-label="View '+html.escape(name)+' website (opens in a new tab)">'
  '<div class="selected-project-image"><img src="'+project_preview(i)+'" alt="'+html.escape(name)+' website screenshot" width="800" height="600" loading="lazy" decoding="async"></div>'
  '<div class="selected-project-caption"><h3>'+html.escape(name)+'</h3><span class="selected-project-number">'+num+'</span></div>'
  '<p class="selected-project-category">'+html.escape(('Book keeping' if i==0 else category).upper())+'</p></a>'
  for i,(num,name,category,url) in enumerate(portfolio_projects[:6]))
 return '<section class="work-section section" id="selected-work"><div class="section-heading"><div><span class="eyebrow">SELECTED WORK</span><h2>Recent projects.<br><em>Different businesses. Clearer websites.</em></h2></div><div class="work-heading-side"><p>A small selection of public project references across trades, services, retail and professional businesses.</p><a class="text-link" href="/portfolio/">All projects '+arrow+'</a></div></div><div class="work-grid">'+cards+'</div><div class="work-footer"><span>PUBLIC PROJECT REFERENCES</span><a class="button outline" href="/designs/">Explore full design catalogue '+arrow+'</a></div></section>'
def window_mock(compact=False):
 return '<div class="browser-window '+('mini-window' if compact else '')+'"><div class="browser-bar"><span class="traffic-lights">● ● ●</span><span>yourbusiness.com.au</span></div><div class="browser-content"><div class="demo-nav"><strong>YOUR BUSINESS</strong><span>Services &nbsp; About &nbsp; Contact</span></div><div class="demo-hero"><span>GOOD WORK. GREAT FIRST IMPRESSIONS.</span><h3>Your business.<br>Your next chapter.</h3><p>A clear website. An easier way to connect.</p><a href="/website-packages/">Explore website options ↗</a></div><div class="demo-grid"><a href="/website-packages/">01<br><strong>What you do</strong></a><a href="/website-redesign/">02<br><strong>Why choose you</strong></a><a href="/contact/">03<br><strong>Let’s talk</strong></a></div></div></div>'
def home():
 return '<main><section class="hero"><div class="hero-grid"><div class="hero-copy"><div class="eyebrow">WEB DESIGN · SEO · AI MARKETING</div><h1>Websites that look <em>professional.</em><br>Built to help your business <em>grow.</em></h1><p>Small business web design for Sydney and beyond. A beautiful website, a clearer search strategy and practical AI support—all built around your next chapter.</p><div class="hero-actions"><a class="button" href="/contact/">Get a Website Quote →</a><a class="button outline" href="/website-packages/">Explore Our Services</a></div><div class="hero-facts"><div><strong>Since 2017</strong><span>Web Solution Sydney</span></div><div><strong>Australia-wide</strong><span>Remote delivery & support</span></div><div><strong>Your business</strong><span>At the heart of every page</span></div></div></div><div class="hero-composition"><div class="float-label float-one"><span>▣</span> Web Design</div><div class="float-label float-two"><span>⌕</span> Search Ready</div><div class="float-label float-three"><span>✧</span> AI Marketing</div><div class="mobile-chip">✓ &nbsp; Mobile-friendly design</div><div class="back-window">'+window_mock(True)+'</div><div class="front-window">'+window_mock()+'</div><div class="demo-caption">ILLUSTRATIVE WEBSITE LAYOUT</div></div></div></section><section class="services section" id="services"><div class="section-heading centered"><div><span class="eyebrow">WHAT WE DO</span><h2>Everything you need.<br>A <em>clearer way forward.</em></h2></div><p>A strong website is the beginning. Choose the support that fits the stage your business is at.</p></div><div class="service-explorer"><div class="service-options" role="tablist" aria-label="Explore our services">'+''.join(f'<button class="service-option" id="tab-{i}" type="button" role="tab" aria-selected="{str(i==0).lower()}" aria-controls="panel-{i}" tabindex="{0 if i==0 else -1}"><span class="option-icon">{icon}</span><span><small>{n} /</small><strong>{label}</strong><span>{d}</span></span><b>↗</b></button>' for i,(n,t,d,label,p,icon) in enumerate(services))+'</div><div class="service-panels">'+''.join(f'<section class="service-panel" role="tabpanel" id="panel-{i}" aria-labelledby="tab-{i}" {"hidden" if i else ""}><div class="panel-icon">{icon}</div><span class="eyebrow">{n} / BUILT AROUND YOUR BUSINESS</span><h3>{t}</h3><p>{d}</p><div class="panel-checks">'+''.join('<span>✓ &nbsp; '+x+'</span>' for x in checks[i])+f'</div><a class="button" href="{p}">{label} →</a></section>' for i,(n,t,d,label,p,icon) in enumerate(services))+'</div></div></section><section class="design-section section"><div><span class="eyebrow">WEBSITE DESIGN</span><h2>A better first impression.<br><em>A more useful website.</em></h2><p>Make it easy for customers to understand what you do, see what makes your business different and take the next step.</p><div class="design-benefits"><div><span>▧</span><section><h3>Designed around your business</h3><p>Your services and customer needs shape the pages.</p></section></div><div><span>▣</span><section><h3>Comfortable on every screen</h3><p>Clear content and contact options on mobile and desktop.</p></section></div><div><span>⌕</span><section><h3>Search foundations from the start</h3><p>Descriptive pages, useful content and sensible internal links.</p></section></div></div><a class="button" href="/website-packages/">Explore Website Packages →</a></div><div class="design-photo"><img src="/assets/sydney.jpg" alt="Sydney Opera House and Harbour Bridge" width="1800" height="1011" loading="lazy"><div class="photo-note"><span>SYDNEY & BEYOND</span><h3>Built for your market.<br><em>Ready for your next move.</em></h3></div><div class="photo-tag">Established in 2017 ↗</div></div></section><section class="ai-feature section"><div><span class="eyebrow">AI MARKETING</span><h2>Make your website<br>a <em>smarter business tool.</em></h2><p>Answer common questions, organise enquiries and prepare useful content. Start with one practical task and build from there.</p><ul><li>Chatbots using approved business information</li><li>Enquiry routing and follow-up workflows</li><li>Content preparation with human review</li></ul><a class="button" href="/ai-marketing/">Explore AI Marketing →</a></div><div class="ai-example"><div class="example-header"><span class="panel-icon">✧</span><div><strong>A simpler customer journey</strong><span>Example enquiry workflow</span></div></div><div class="workflow-step"><span>01</span><div><strong>A visitor asks a question</strong><p>“Do you build websites for small businesses?”</p></div></div><div class="workflow-step"><span>02</span><div><strong>Useful information comes first</strong><p>Explain the service using approved business details.</p></div></div><div class="workflow-step"><span>03</span><div><strong>A person takes the next step</strong><p>Pass the enquiry to your business for a tailored response.</p></div></div><a href="/contact/">Discuss a setup for your business →</a></div></section><section class="process section"><div class="section-heading centered"><div><span class="eyebrow">HOW WE WORK</span><h2>A clear <em>process.</em><br>From first idea to launch.</h2></div></div><div class="steps"><div><span>01</span><h3>Understand & plan</h3><p>We work through your services, customers and goals, then agree on a useful project scope.</p></div><div><span>02</span><h3>Design & create</h3><p>Your content and design come together. You review the pages before they go live.</p></div><div><span>03</span><h3>Launch & support</h3><p>We check the website and contact flow, arrange the launch and explain your ongoing options.</p></div></div></section><section class="faq-section section"><div class="section-heading centered"><div><span class="eyebrow">A FEW USEFUL ANSWERS</span><h2>Questions, <em>answered.</em></h2></div></div>'+''.join('<details><summary>'+q+'</summary><p>'+a+'</p></details>' for q,a in faqs)+'</section>'+cta()+'</main>'
def home_with_industries():
 result=home().replace('<section class="design-section section">',industry_strip()+selected_work()+'<section class="design-section section">',1)
 result=re.sub(r'<h1>.*?</h1>','<h1>Web design for<br><em>Sydney businesses.</em><br>Built for your next chapter.</h1>',result,count=1)
 result=result.replace('INDUSTRY PAGES','WEBSITES FOR YOUR BUSINESS').replace('Explore page ↗','Explore websites ↗')
 result=result.replace('Start with a relevant page for your industry, then shape the rest of the website around your services, customers and goals.','Explore website design for your business, shaped around your services, customers and goals.')
 return result

checks=[['Mobile-friendly pages','Clear service content','SEO foundations','An agreed project scope'],['Hosting arrangements','Platform-specific care','Defined support','Clear recurring costs'],['Keyword & page planning','Content improvements','Technical checks','Meaningful reporting'],['Website chatbots','Enquiry workflows','Content preparation','Human review']]
faqs=[('Can you help if I already have a website?','Yes. We can review your current website and scope improvements or a redesign around what your business needs.'),('Does the website include ongoing SEO?','The website build includes agreed SEO foundations. Ongoing keyword research, publishing and SEO work are scoped separately.'),('Do you work with businesses outside Sydney?','Yes. We work remotely with small businesses across Australia.'),('How much will my website cost?','Your quote depends on the pages, content and features required. Share your requirements for a project-specific quote.')]

def cta():return '<section class="cta section"><div class="cta-box"><span class="eyebrow">LET’S CREATE YOUR NEXT CHAPTER</span><h2>Ready to build<br><em>something better?</em></h2><p>Tell us what your business needs. We’ll help you choose the right starting point.</p><div class="hero-actions"><a class="button" href="/contact/">Get a Website Quote →</a><a class="button outline" href="tel:+61420102599">Call 0420 102 599</a></div></div></section>'

def content_html(content):
 out=[]
 for block in re.split(r'\n\s*\n',content):
  block=block.strip()
  if not block:continue
  if block.startswith('# '):continue
  if re.match(r'\*\*(Primary button|Secondary|Button|Footer|Form labels|Service choices|Success message|Error message)',block):continue
  if block.startswith('## '):out.append('<h2>'+inline(block[3:])+'</h2>')
  elif all(line.startswith('- ') for line in block.splitlines()):out.append('<ul>'+''.join('<li>'+inline(line[2:])+'</li>' for line in block.splitlines())+'</ul>')
  else:out.append('<p>'+inline(block).replace('\n','<br>')+'</p>')
 return ''.join(out)
def contact_form():return '''<section class="contact-section"><div class="contact-grid"><div class="contact-info"><span class="eyebrow">GET IN TOUCH</span><h2>Let’s start<br><em>a conversation.</em></h2><p>Tell us about your business and what you need. We’ll get back to you within one business day.</p><div class="contact-info-details"><div class="contact-info-item"><div class="ci-icon">☏</div><div><span class="contact-info-label">PHONE</span><a href="tel:+61420102599">0420 102 599</a></div></div><div class="contact-info-item"><div class="ci-icon">✉</div><div><span class="contact-info-label">EMAIL</span><a href="mailto:ryan@websolutionsydney.com.au">ryan@websolutionsydney.com.au</a></div></div><div class="contact-info-item"><div class="ci-icon">⌖</div><div><span class="contact-info-label">LOCATION</span><span>Sydney, Australia</span></div></div><div class="contact-info-item"><div class="ci-icon">⏱</div><div><span class="contact-info-label">RESPONSE TIME</span><span>Usually within one business day</span></div></div></div><div class="contact-trust"><span>✓&nbsp; Established 2017</span><span>✓&nbsp; Australia-wide</span><span>✓&nbsp; No obligation</span></div></div><div class="contact-card"><div id="form-success" class="form-success" hidden><div class="success-icon">✓</div><h3>Enquiry sent — thank you!</h3><p>Your enquiry has been received. We’ll review it and respond within one business day. If you need urgent help, call <a href="tel:+61420102599">0420 102 599</a>.</p><button class="button outline" type="button" id="send-another">Send another enquiry</button></div><form id="enquiry-form" class="contact-form" novalidate><div class="field"><label for="cf-name">Full name <span class="req">*</span></label><input id="cf-name" name="name" autocomplete="name" placeholder="Jane Smith" maxlength="100" required></div><div class="field"><label for="cf-email">Email address <span class="req">*</span></label><input id="cf-email" name="email" type="email" autocomplete="email" placeholder="jane@example.com.au" maxlength="254" required></div><div class="field"><label for="cf-phone">Phone number</label><input id="cf-phone" name="phone" type="tel" autocomplete="tel" placeholder="04XX XXX XXX" maxlength="20"></div><div class="field"><label for="cf-business">Business / company name</label><input id="cf-business" name="business" autocomplete="organization" placeholder="Smith & Co" maxlength="150"></div><div class="field"><label for="cf-service">Service required <span class="req">*</span></label><select id="cf-service" name="service" required><option value="">Select a service…</option><option value="Website Design & Development">Website Design &amp; Development</option><option value="Website Redesign">Website Redesign</option><option value="E-Commerce Website">E-Commerce Website</option><option value="SEO & Digital Marketing">SEO &amp; Digital Marketing</option><option value="AI Chatbot & Website Automation">AI Chatbot &amp; Website Automation</option><option value="App Development">App Development</option><option value="Logo & Graphic Design">Logo &amp; Graphic Design</option><option value="Website Hosting & Maintenance">Website Hosting &amp; Maintenance</option><option value="Other">Other</option></select></div><div class="field"><label for="cf-budget">Project budget</label><select id="cf-budget" name="budget"><option value="">Select a range…</option><option value="Under $2,000">Under $2,000</option><option value="$2,000 – $5,000">$2,000 – $5,000</option><option value="$5,000 – $10,000">$5,000 – $10,000</option><option value="$10,000 – $25,000">$10,000 – $25,000</option><option value="$25,000+">$25,000+</option><option value="Not sure yet">Not sure yet</option></select></div><div class="field field-full"><label for="cf-website">Current website (optional)</label><input id="cf-website" name="website" type="url" placeholder="https://yourbusiness.com.au" maxlength="500"></div><div class="field field-full"><label for="cf-message">Project details / message <span class="req">*</span></label><textarea id="cf-message" name="message" rows="5" minlength="10" maxlength="4000" required placeholder="Tell us about your business, what you need, and any timeline you have in mind…"></textarea><div class="char-count"><span id="char-count">0</span> / 4000</div></div><div class="field field-full" id="enquiry-verification" hidden></div><label class="enquiry-trap" aria-hidden="true">Leave this blank<input name="company_url" tabindex="-1" autocomplete="off"></label><div id="form-error" class="form-error" role="alert" hidden></div><div class="form-actions"><button class="button" type="submit" id="submit-btn"><span class="btn-label">Send Enquiry</span></button><p class="form-note">We respect your privacy. Read our <a href="/privacy/">privacy notice</a>.<br>Prefer email? <a href="mailto:ryan@websolutionsydney.com.au">ryan@websolutionsydney.com.au</a></p></div></form></div></div></section>'''
def portfolio_page():
 cards=''.join('<a class="portfolio-card" data-category="'+html.escape(category.lower(),quote=True)+'" href="'+url+'" target="_blank" rel="noopener noreferrer">'+('<div class="portfolio-thumb"><img src="'+project_preview(i,url)+'" alt="'+html.escape(name)+' website screenshot" loading="lazy" width="800" height="600"><span>'+num+' / '+html.escape(category.upper())+'</span></div>' if project_preview(i,url) else '')+'<div class="portfolio-card-caption"><h2>'+html.escape(name)+'</h2><span>'+num+'</span></div><div class="portfolio-card-meta"><p>'+html.escape(category.upper())+'</p><small>'+html.escape(url.replace('https://','').replace('http://','').replace('www.','').rstrip('/'))+'</small></div></a>' for i,(num,name,category,url) in enumerate(portfolio_projects))
 categories=[]
 for _,_,category,_ in portfolio_projects:
  if category not in categories: categories.append(category)
 filters='<button class="portfolio-filter is-active" type="button" data-filter="all" aria-pressed="true">ALL</button>'+''.join('<button class="portfolio-filter" type="button" data-filter="'+html.escape(category.lower(),quote=True)+'" aria-pressed="false">'+html.escape(category.upper())+'</button>' for category in categories)
 return '<main><section class="portfolio-hero page-hero section"><div class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span><span>Portfolio</span></div><span class="eyebrow">PORTFOLIO · 20 PROJECTS</span><h1>The work<br><em>speaks for itself.</em></h1></section><section class="section portfolio-section"><div class="portfolio-filters" role="group" aria-label="Filter portfolio projects">'+filters+'</div><div class="portfolio-grid">'+cards+'</div><div class="portfolio-catalogue-link"><a class="button outline" href="/designs/">Explore full design catalogue '+arrow+'</a></div></section><section class="section catalogue-callout"><div><span class="eyebrow">YOUR BUSINESS COULD BE NEXT</span><h2>Yours could be<br><em>the next project.</em></h2></div><a class="button" href="/contact/">Start a project '+arrow+'</a></section>'+cta()+'</main>'
def designs_page():
 categories=''.join('<a class="catalogue-card" href="/portfolio/"><span>'+num+' /</span><h2>'+html.escape(title)+'</h2><p>'+html.escape(description)+'</p><b>View related work '+arrow+'</b></a>' for num,title,description in catalogue_categories)
 return '<main><section class="page-hero section"><div class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span><span>Design catalogue</span></div><span class="eyebrow">WEBSITE DESIGN / CATALOGUE</span><h1>More ways to shape<br><em>your next website.</em></h1><div class="page-intro"><p>A working catalogue of website directions organised by the kinds of businesses and projects we support. Use it as inspiration, then shape the brief around your own customers and services.</p></div></section><section class="section catalogue-section"><div class="catalogue-heading"><span class="eyebrow">BROWSE BY DIRECTION</span><h2>Find a starting point<br><em>that fits your business.</em></h2></div><div class="catalogue-grid">'+categories+'</div></section><section class="section catalogue-note"><div><span class="eyebrow">HAVE A DIFFERENT IDEA?</span><h2>Good. Let’s make<br><em>it yours.</em></h2></div><div><p>The examples are starting points, not fixed templates. Tell us what you do, what customers need to understand and what the website should help them do next.</p><a class="button" href="/contact/">Discuss your website '+arrow+'</a></div></section>'+cta()+'</main>'
def inner(p):
 if p['url']=='/portfolio/':return portfolio_page()
 if p['url']=='/designs/':return designs_page()
 isguide=p['url'].startswith('/guides/')
 eyebrow='PRACTICAL BUSINESS GUIDES' if isguide else 'WEB SOLUTION SYDNEY / '+p['url'].strip('/').replace('-',' ').upper()
 leadblocks=re.split(r'^## ',p['content'],maxsplit=1,flags=re.M)
 intro=content_html(leadblocks[0])
 body=content_html('## '+leadblocks[1]) if len(leadblocks)>1 else ''
 if isguide:
  for text,path in [('website packages','/website-packages/'),('hosting and care','/website-hosting/'),('website redesign','/website-redesign/'),('small-business SEO','/seo-services/')]:
   body=body.replace(text,'<a href="'+path+'">'+text+'</a>',1)
 if p['url']=='/contact/':eyebrow='WEB SOLUTION SYDNEY / CONTACT';intro='<p>Have a project in mind? We’d love to hear about it. Whether you need a new website, a redesign, SEO support or practical AI tools, share your details below and we’ll respond within one business day.</p>';body=''
 links=''.join('<a href="'+path+'">'+html.escape(page_by_url[path]['title'].split(' | ')[0])+' '+arrow+'</a>' for path in p['keywords'].get('related',[]) if path!=p['url'])
 related='<aside class="article-aside"><span class="eyebrow">LET’S TALK ABOUT IT</span><h3>A practical next step for your business.</h3><p>Tell us what you need. We’ll help turn it into a clear project scope.</p><a class="button" href="/contact/">Discuss your project ↗</a><hr>'+links+'</aside>'
 breadcrumbs='<div class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true"> / </span><span>'+html.escape(p['title'].split(' | ')[0])+'</span></div>'
 article='<div class="section article-layout"><article class="prose">'+body+'</article>'+related+'</div>'+cta()
 if p['url']=='/privacy/':article='<article class="section prose privacy-content">'+body+'</article>'
 contact_cta='<section class="contact-closing"><div class="contact-closing-box"><span class="eyebrow">READY WHEN YOU ARE</span><h2>Prefer to talk directly?</h2><p>Call <a href="tel:+61420102599">0420 102 599</a> or email <a href="mailto:ryan@websolutionsydney.com.au">ryan@websolutionsydney.com.au</a>. We’re ready to help your business take its next step.</p></div></section>'
 return '<main><section class="page-hero section">'+breadcrumbs+'<span class="eyebrow">'+eyebrow+'</span><h1>'+inline(p['heading'])+'</h1><div class="page-intro">'+intro+'</div></section>'+(contact_form()+contact_cta if p['url']=='/contact/' else article)+'</main>'
favicon='/assets/favicon.png'
def seo_head(p):
 canonical='https://websolutionsydney.com.au'+p['url']
 data={"@context":"https://schema.org","@graph":[
  {"@type":"Organization","@id":"https://websolutionsydney.com.au/#organization","name":"Web Solution Sydney","url":"https://websolutionsydney.com.au/","logo":"https://websolutionsydney.com.au/assets/logo.png","telephone":"+61420102599","email":"ryan@websolutionsydney.com.au","foundingDate":"2017","areaServed":{"@type":"Country","name":"Australia"}},
  {"@type":"WebSite","@id":"https://websolutionsydney.com.au/#website","url":"https://websolutionsydney.com.au/","name":"Web Solution Sydney","publisher":{"@id":"https://websolutionsydney.com.au/#organization"},"inLanguage":"en-AU"},
  {"@type":"WebPage","@id":canonical+'#webpage',"url":canonical,"name":p['title'],"description":p['meta'],"isPartOf":{"@id":"https://websolutionsydney.com.au/#website"},"about":{"@id":"https://websolutionsydney.com.au/#organization"},"inLanguage":"en-AU"}
 ]}
 if p['url'] in [path for _,path in website_pages+growth_pages]:
  data['@graph'].append({"@type":"Service","@id":canonical+'#service',"name":p['keywords']['primary'],"url":canonical,"provider":{"@id":"https://websolutionsydney.com.au/#organization"},"areaServed":{"@type":"Country","name":"Australia"}})
 if p['url']!='/':
  data['@graph'].append({"@type":"BreadcrumbList","@id":canonical+'#breadcrumb',"itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://websolutionsydney.com.au/"},{"@type":"ListItem","position":2,"name":p['title'].split(' | ')[0],"item":canonical}]})
  data['@graph'][2]['breadcrumb']={"@id":canonical+'#breadcrumb'}
 if p['url'].startswith('/guides/'):
  data['@graph'].append({"@type":"Article","@id":canonical+'#article',"headline":p['heading'],"mainEntityOfPage":{"@id":canonical+'#webpage'},"author":{"@id":"https://websolutionsydney.com.au/#organization"},"publisher":{"@id":"https://websolutionsydney.com.au/#organization"},"inLanguage":"en-AU"})
 return '<meta property="og:type" content="website"><meta property="og:site_name" content="Web Solution Sydney"><meta property="og:locale" content="en_AU"><meta property="og:title" content="'+html.escape(p['title'],quote=True)+'"><meta property="og:description" content="'+html.escape(p['meta'],quote=True)+'"><meta property="og:url" content="'+canonical+'"><meta property="og:image" content="https://websolutionsydney.com.au/assets/sydney.jpg"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="'+html.escape(p['title'],quote=True)+'"><meta name="twitter:description" content="'+html.escape(p['meta'],quote=True)+'"><meta name="twitter:image" content="https://websolutionsydney.com.au/assets/sydney.jpg"><script type="application/ld+json">'+json.dumps(data,separators=(',',':'))+'</script>'
asset_version=hashlib.sha256((OUT/'styles.css').read_bytes()+(OUT/'site.js').read_bytes()).hexdigest()[:12]
for p in pages:
 document='<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#e5f7fc"><title>'+html.escape(p['title'])+'</title><meta name="description" content="'+html.escape(p['meta'],quote=True)+'"><link rel="canonical" href="https://websolutionsydney.com.au'+p['url']+'">'+seo_head(p)+'<link rel="icon" type="image/png" sizes="512x512" href="'+favicon+'"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="stylesheet" href="/styles.css"><script src="/site.js" defer></script></head><body><a class="skip" href="#content">Skip to content</a>'+header(p['url'])+'<div id="content">'+(home_with_industries() if p['url']=='/' else inner(p))+'</div>'+footer()+'</body></html>'
 document=document.replace('/styles.css"','/styles.css?v='+asset_version+'"').replace('/site.js"','/site.js?v='+asset_version+'"')
 document=document.replace('<span>Serving Australian businesses remotely.</span>','<a href="/privacy/">Privacy</a><span>Serving Australian businesses remotely.</span>')
 dest=OUT/p['url'].strip('/')/'index.html' if p['url']!='/' else OUT/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(document)
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://websolutionsydney.com.au'+p['url']+'</loc></url>' for p in pages)+'</urlset>')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://websolutionsydney.com.au/sitemap.xml\n')
(OUT/'404.html').write_text('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found | Web Solution Sydney</title><link rel="icon" type="image/png" sizes="512x512" href="'+favicon+'"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="stylesheet" href="/styles.css"></head><body>'+header('')+'<main class="section page-hero"><span class="eyebrow">404 / PAGE NOT FOUND</span><h1>Let’s get you<br>back on track.</h1><a class="button" href="/">Back to home ↗</a></main>'+footer()+'</body></html>')
error_file=OUT/'404.html'
error_html=error_file.read_text().replace('<title>','<meta name="robots" content="noindex"><script src="/site.js?v='+asset_version+'" defer></script><title>',1)
error_file.write_text(error_html.replace('/styles.css"','/styles.css?v='+asset_version+'"'))
# Cloudflare Pages advanced-mode Worker. Keeping the API route inside the build
# output ensures it is deployed even when the dashboard does not detect the
# repository-level functions directory.
enquiry_worker=(ROOT/'server'/'enquiry.mjs').read_text().replace('export async function handleEnquiry','async function handleEnquiry',1)
enquiry_worker+='''\n\nexport default {
  async fetch(request, env) {
    const pathname = new URL(request.url).pathname;
    if (pathname === '/api/enquiry' || pathname === '/api/enquiry/') {
      return handleEnquiry(request, env);
    }
    return env.ASSETS.fetch(request);
  }
};
'''
(OUT/'_worker.js').write_text(enquiry_worker)

assets_dir=OUT/'assets'
assets_dir.mkdir(parents=True,exist_ok=True)
asset_sources={
 'logo.png':'https://websolutionsydney.com.au/assets/logo.png',
 'favicon.png':'https://websolutionsydney.com.au/assets/favicon.png',
 'apple-touch-icon.png':'https://websolutionsydney.com.au/assets/apple-touch-icon.png',
 'sydney.jpg':'https://websolutionsydney.com.au/assets/sydney.jpg',
}
for name,url in asset_sources.items():
 target=assets_dir/name
 if target.exists() and target.stat().st_size>0:
  continue
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=30) as r:
   data=r.read()
   if len(data)>0:target.write_bytes(data)
 except Exception as e:
  print('Warning: could not download',name,'-',e)

print('Generated',len(pages),'pages')
