from django.core.management.base import BaseCommand
from locations.models import AboutPost


class Command(BaseCommand):
    help = 'Create sample about posts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--post',
            type=str,
            choices=['environmental', 'meaningful-change', 'transparent-leadership', 'journey-achievements', 'principles-guide-work', 'team-behind-accessadvisr'],
            default='environmental',
            help='Which post to create (environmental, meaningful-change, transparent-leadership, journey-achievements, principles-guide-work, or team-behind-accessadvisr)'
        )

    def handle(self, *args, **options):
        post_type = options.get('post', 'environmental')
        
        if post_type == 'meaningful-change':
            self.create_meaningful_change_post()
        elif post_type == 'transparent-leadership':
            self.create_transparent_leadership_post()
        elif post_type == 'journey-achievements':
            self.create_journey_achievements_post()
        elif post_type == 'principles-guide-work':
            self.create_principles_guide_work_post()
        elif post_type == 'team-behind-accessadvisr':
            self.create_team_behind_accessadvisr_post()
        else:
            self.create_environmental_post()
    
    def create_meaningful_change_post(self):
        content = """
        <h2>Empowering People Through Accessibility and Awareness</h2>
        
        <p>At AccessAdvisr, we believe that accessibility is more than just a feature, it is a fundamental right that shapes how people experience the world. Through accurate, user-driven accessibility reviews and valuable resources, we empower individuals to make informed decisions about the spaces they visit, the services they use, and the communities they engage with. Our mission is to ensure that everyone, regardless of ability, can navigate the world with confidence, independence, and dignity.</p>
        
        <p>Our platform serves as a trusted source of information for people with disabilities, carers, families, and accessibility advocates. By gathering honest, real-world feedback from users, AccessAdvisr paints an authentic picture of how accessible venues, services, and facilities truly are. This crowdsourced insight helps bridge the gap between intention and reality, showing where accessibility works well and where improvement is still needed. Every review submitted contributes to a growing network of shared knowledge that benefits communities locally and globally.</p>
        
        <p>We understand that accessibility means different things to different people. That's why we go beyond simply evaluating ramps and doorways. Our reviews consider the entire user experience, from sensory environments and staff attitudes to digital usability and transport links. By highlighting these factors, we help businesses, governments, and organisations understand the full scope of accessibility and the real impact it has on people's lives. This detailed and human-centred approach ensures that inclusion is not treated as an afterthought, but as a standard of quality and respect.</p>
        
        <p>Our work extends far beyond information-sharing. AccessAdvisr actively raises awareness about accessibility challenges and opportunities through education, advocacy, and collaboration. We believe that progress begins with understanding, so we provide resources that help individuals and organisations learn how to make their environments more inclusive. From practical accessibility guides to awareness campaigns, we strive to make knowledge accessible, actionable, and inspiring.</p>
        
        <p>One of the most powerful outcomes of our work is the sense of empowerment it creates. When people have access to accurate, trustworthy information, they gain the ability to make choices that suit their needs. Whether it's choosing a restaurant, planning a trip, or attending an event, AccessAdvisr helps users make these decisions with confidence. That empowerment translates into freedom, the freedom to explore, to connect, and to participate fully in life's opportunities.</p>
        
        <p>At the same time, our platform serves as a catalyst for positive change within the wider community. When businesses see how accessibility influences people's decisions, they gain valuable insights into how to improve their services. Our data and feedback highlight practical ways organisations can become more inclusive, often leading to meaningful action and measurable improvements. Through these outcomes, AccessAdvisr contributes not only to individual empowerment but also to systemic change, shaping a world that works better for everyone.</p>
        
        <p>Inclusivity is at the heart of everything we do. We are driven by the belief that accessibility should not be limited to a few, it should be a universal standard that benefits all. By connecting users, advocates, and businesses in a shared mission, AccessAdvisr fosters collaboration and understanding across diverse communities. We celebrate progress, acknowledge challenges, and continue to champion the voices of people with disabilities worldwide.</p>
        
        <p>Ultimately, our goal is simple but powerful: to create a world where accessibility is visible, valued, and verified by real experiences. Every review, every story, and every connection brings us closer to that vision. Through collective effort and shared responsibility, we are building a global community that recognises accessibility not as a box to tick, but as a continuous journey toward equality and respect.</p>
        
        <p>At AccessAdvisr, we are proud to stand at the intersection of technology, community, and inclusion, empowering people to live, travel, and participate without barriers. Together, we're not just improving access; we're transforming how the world sees and supports accessibility.</p>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='making-meaningful-change',
            defaults={
                'title': 'Making Meaningful Change',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'Making Meaningful Change'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))
    
    def create_transparent_leadership_post(self):
        content = """
        <h2>Our Commitment to Good Governance</h2>
        
        <p>At AccessAdvisr, we believe that strong governance is the foundation of lasting impact. As an organisation committed to accessibility, inclusion, and social responsibility, we understand that how we operate is just as important as what we achieve. Our governance principles ensure that every decision we make is guided by integrity, accountability, and transparency. These values underpin our mission, shape our culture, and build the trust that our users, partners, and communities place in us every day.</p>
        
        <p>Good governance at AccessAdvisr is not simply about compliance, it is about doing what is right, even when it goes beyond what is required. We hold ourselves to the highest ethical standards, ensuring that our actions reflect our values and contribute to a fair and responsible organisation. Through open communication, responsible leadership, and continuous evaluation, we maintain a governance structure that is both effective and adaptable to the evolving needs of our stakeholders.</p>
        
        <h3>Ethical Management and Leadership</h3>
        
        <p>AccessAdvisr's leadership team is deeply committed to ethical management practices. Every decision we take is guided by our organisational code of conduct, which emphasises honesty, fairness, respect, and accountability. We promote a culture where ethical considerations are not just discussed but actively integrated into strategic planning and daily operations. From safeguarding user data to ensuring accessibility reviews remain unbiased and accurate, our management processes are designed to protect the integrity of both our mission and our community.</p>
        
        <h3>Transparency and Accountability</h3>
        
        <p>Transparency is at the heart of our operations. We believe that open communication builds confidence, and confidence fosters collaboration. We are committed to sharing information clearly, whether about our policies, partnerships, or performance, so that our community understands how we operate and what drives our decisions. This openness extends to our digital practices as well; we prioritise clarity in how we collect, use, and safeguard information, ensuring that users can trust our platform as a reliable and secure source.</p>
        
        <p>Accountability is equally essential. Every member of our team understands their role in upholding the principles that define AccessAdvisr. We regularly assess our processes and performance to ensure that we are meeting both our internal standards and the expectations of our stakeholders. By maintaining rigorous reporting structures and feedback systems, we can identify areas for improvement and act swiftly and responsibly when change is needed.</p>
        
        <h3>Building Trust and Partnership</h3>
        
        <p>Our commitment to governance goes beyond internal operations, it extends to how we engage with our partners, collaborators, and community. We seek to build relationships based on mutual trust and respect, ensuring that everyone we work with shares our dedication to ethical conduct and inclusive progress. This approach strengthens our impact, helping us to create partnerships that are transparent, equitable, and aligned with our social purpose.</p>
        
        <p>Trust is earned through consistency, and at AccessAdvisr, we strive to demonstrate our values in every interaction. Whether collaborating with accessibility advocates, supporting local initiatives, or working with global organisations, we uphold the same principles of integrity and fairness that guide our internal operations.</p>
        
        <h3>Continuous Improvement</h3>
        
        <p>Governance is not a static concept, it evolves as our organisation grows and as the world around us changes. We continuously review and refine our governance practices to ensure they remain relevant, resilient, and responsive. This includes adopting new technologies, frameworks, and policies that enhance oversight, protect stakeholder interests, and strengthen ethical decision-making.</p>
        
        <p>At AccessAdvisr, we see governance as a living commitment, one that ensures our organisation remains trustworthy, transparent, and aligned with our mission to improve accessibility for all. By embedding good governance into every aspect of our work, we create a foundation for sustainable growth, social impact, and meaningful collaboration.</p>
        
        <p>Our promise is simple yet powerful: to operate with integrity, to be accountable for our actions, and to remain transparent in all we do. In doing so, we continue to earn the confidence of our community and partners, today, tomorrow, and for years to come.</p>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='transparent-and-accountable-leadership',
            defaults={
                'title': 'Transparent and Accountable Leadership',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'Transparent and Accountable Leadership'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))
    
    def create_journey_achievements_post(self):
        content = """
        <h2>Our Journey: From a Small Initiative to a Global Movement for Accessibility</h2>
        
        <p>AccessAdvisr's story began with a simple yet powerful idea, to make the world more accessible, one experience at a time. What started as a small initiative aimed at addressing everyday accessibility challenges has evolved into a globally recognised platform dedicated to empowering people with disabilities. Our journey has been defined by innovation, collaboration, and an unwavering commitment to improving lives through inclusion and awareness.</p>
        
        <p>From the outset, we recognised a significant gap in how accessibility information was shared and understood. People with disabilities often faced uncertainty when visiting new places or using unfamiliar services, a challenge that could limit independence, confidence, and participation in community life. AccessAdvisr was created to bridge that gap. Our goal was clear: to provide accurate, user-driven insights that enable people to make informed decisions about where to go, what to expect, and how to navigate the world more freely.</p>
        
        <p>What began as a small-scale initiative has since grown into a trusted, international platform that connects individuals, communities, and organisations in the shared mission of accessibility and inclusion. Through the power of technology and authentic user experiences, AccessAdvisr has built a global network where people can review, share, and discover accessibility information across diverse environments, from public spaces and transportation to digital platforms and hospitality venues.</p>
        
        <p>Our success is rooted in our dedication to people. Every review, resource, and partnership we create is designed with empathy and purpose. We listen to the voices of our users, the individuals whose lived experiences shape our understanding of accessibility. Their feedback guides our innovation, ensuring that AccessAdvisr remains practical, inclusive, and deeply human. By combining personal insight with data-driven analysis, we are helping to redefine how society measures and values accessibility.</p>
        
        <p>Innovation has played a crucial role in our evolution. As technology has advanced, so too has our ability to make accessibility information more interactive, accurate, and widely available. We have continually refined our platform to ensure that it remains intuitive, responsive, and globally relevant. From mobile-friendly tools to intelligent data mapping, every upgrade we introduce is designed to improve usability and extend our reach to more people, in more places, than ever before.</p>
        
        <p>But growth for us is not only about scale, it's about impact. Over the years, AccessAdvisr has become a catalyst for change. Our work has inspired businesses, local authorities, and organisations to prioritise accessibility as an essential part of their culture and operations. By highlighting both challenges and success stories, we have helped spark awareness and drive meaningful improvements in public and private spaces alike.</p>
        
        <p>We are proud that our journey reflects a deep and unwavering commitment to inclusion. From local community projects to global partnerships, AccessAdvisr continues to champion equality, respect, and independence for people with disabilities. Our mission has always been about more than information, it's about empowerment. By giving people the tools to share their experiences and access reliable insights, we are fostering a world where accessibility is recognised not as a special consideration, but as a universal standard.</p>
        
        <p>Today, AccessAdvisr stands as a global platform, a community of advocates, innovators, and everyday heroes working together toward a more inclusive future. Yet, we remain grounded in our original vision: to make life easier, fairer, and more connected for everyone, regardless of ability.</p>
        
        <p>Our journey is far from over. As we look ahead, we continue to embrace innovation, collaboration, and compassion as the driving forces behind our mission. The challenges of accessibility may evolve, but our purpose remains constant, to ensure that every person, everywhere, has the freedom to participate fully in society without barriers.</p>
        
        <p>At AccessAdvisr, we are proud of how far we've come, but even more excited about where we're going. From a small initiative to a global movement, our journey is a testament to what can be achieved when dedication, technology, and human empathy come together for a common cause, building a world that is truly accessible to all.</p>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='our-journey-and-achievements',
            defaults={
                'title': 'Our Journey and Achievements',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published',
                'order': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'Our Journey and Achievements'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))
    
    def create_principles_guide_work_post(self):
        content = """
        <h2>Our Core Values: Inclusion, Empowerment, and Integrity</h2>
        
        <p>At AccessAdvisr, inclusion, empowerment, and integrity are not just words, they are the guiding principles that shape every aspect of our organisation. These core values define who we are, how we operate, and the impact we strive to create for people with disabilities around the world. They serve as the foundation for our decisions, the inspiration behind our innovations, and the benchmark against which we measure our success.</p>
        
        <p>Inclusion lies at the heart of our mission. We believe that every individual, regardless of ability, deserves equal opportunities, access, and respect. This belief drives everything we do, from the design of our platform to the way we engage with our users and partners. Inclusion is about more than physical accessibility, it encompasses digital accessibility, social participation, and the cultivation of environments where everyone feels valued and welcomed. By actively listening to the experiences of our community, we ensure that diverse perspectives inform our strategies and initiatives. Inclusion is not merely a goal for AccessAdvisr; it is a mindset that permeates our culture, guiding our interactions and shaping our policies.</p>
        
        <p>Empowerment is another cornerstone of our work. At AccessAdvisr, we aim to give people the knowledge, tools, and confidence to make informed decisions. Through accurate accessibility reviews, practical resources, and educational initiatives, we provide individuals with the means to navigate the world with independence and dignity. Empowerment extends beyond our users to include businesses, organisations, and communities. By equipping them with insights and guidance, we enable meaningful improvements in accessibility that create lasting impact. We believe that empowering people is not just about providing information, it is about fostering confidence, autonomy, and the ability to take action.</p>
        
        <p>Integrity underpins every decision we make. As an organisation committed to trust, accountability, and ethical practice, we hold ourselves to the highest standards of transparency and honesty. Integrity informs the way we collect and present data, the partnerships we establish, and the services we provide. It ensures that our community can rely on AccessAdvisr as a credible and responsible source of information. By consistently acting with integrity, we build trust with our users, partners, and stakeholders, reinforcing the credibility of our platform and the reliability of our guidance.</p>
        
        <p>Together, these three values — inclusion, empowerment, and integrity, create a framework for action that drives both our mission and our culture. They inspire innovation by encouraging us to think creatively about how to break down barriers, reach underserved communities, and design solutions that are effective and meaningful. They guide strategic decisions by ensuring that every initiative aligns with our commitment to social responsibility and positive impact.</p>
        
        <p>At AccessAdvisr, our core values also serve as a standard for excellence. We measure our success not only by the growth of our platform but by the real, tangible improvements we create in the lives of people with disabilities. Every review submitted, every resource developed, and every partnership formed is guided by our dedication to these principles. They remind us that our work is not just operational, it is purposeful, impactful, and transformative.</p>
        
        <p>Ultimately, inclusion, empowerment, and integrity are more than foundational principles; they are the essence of AccessAdvisr's identity. They reflect our promise to serve the disabled community with dedication, respect, and excellence. By living these values every day, we continue to advance our mission of building a world where accessibility is standard, participation is universal, and every individual is empowered to thrive.</p>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='principles-that-guide-our-work',
            defaults={
                'title': 'Principles That Guide Our Work',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published',
                'order': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'Principles That Guide Our Work'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))
    
    def create_team_behind_accessadvisr_post(self):
        content = """
        <p>At AccessAdvisr, we are proud to have a dedicated team of professionals who bring diverse expertise, lived experience, and a shared passion for accessibility. Our team combines technical innovation with real-world understanding of accessibility challenges, ensuring that our platform serves the needs of our community effectively and empathetically.</p>
        
        <div class="team-member-section mb-5" style="margin-top: 3rem;">
            <div class="row align-items-center">
                <div class="col-md-4 mb-4 mb-md-0">
                    <img src="/static/images/about/rob-trent.png" alt="Rob Trent" class="img-fluid rounded" style="width: 100%; max-width: 300px; height: auto;">
                </div>
                <div class="col-md-8">
                    <h3 class="fw-bold mb-3" style="color: #1a2b48; font-size: 1.75rem;">About Rob Trent</h3>
                    <p><strong>Managing Director</strong></p>
                    <p>Rob Trent brings extensive lived experience with disability to his role as Managing Director of AccessAdvisr. His personal journey has shaped his deep understanding of the accessibility challenges that people face in their daily lives, from navigating public spaces to accessing services and opportunities.</p>
                    <p>Beyond his professional responsibilities, Rob is a devoted family man who enjoys traveling with his loved ones. His passion for football reflects his belief in the power of sport to bring people together, regardless of ability. This same spirit of inclusion drives his commitment to making the world more accessible for everyone.</p>
                    <p>Rob's leadership experience spans various sectors, where he has consistently championed accessibility and inclusion. His creative side is evident in his work as a mouth painter, demonstrating that talent and passion know no boundaries. This artistic pursuit reflects his belief that everyone has unique abilities and contributions to make.</p>
                    <p>At AccessAdvisr, Rob is committed to ensuring that the platform remains true to its mission: empowering people with disabilities through accurate, user-driven accessibility information. His leadership is guided by empathy, innovation, and an unwavering dedication to creating positive change in the accessibility landscape.</p>
                </div>
            </div>
        </div>
        
        <div class="team-member-section mb-5" style="margin-top: 3rem;">
            <div class="row align-items-center">
                <div class="col-md-8 mb-4 mb-md-0">
                    <h3 class="fw-bold mb-3" style="color: #1a2b48; font-size: 1.75rem;">About Dr Shah Siddiqui</h3>
                    <p>Dr. Shah Siddiqui is a visionary tech entrepreneur and AI strategist who brings cutting-edge innovation to AccessAdvisr. With a background that spans technology, business, and academic excellence, Dr. Siddiqui has been instrumental in developing the technical infrastructure that makes AccessAdvisr a powerful and user-friendly platform.</p>
                    <p>As an academic innovator, Dr. Siddiqui understands the importance of combining research-driven insights with practical solutions. His expertise in artificial intelligence and data analytics has enabled AccessAdvisr to process and present accessibility information in ways that are both accurate and accessible to users.</p>
                    <p>Dr. Siddiqui is the founder and CEO of several successful organizations, each reflecting his commitment to using technology for social good. His mission aligns perfectly with AccessAdvisr's goals: leveraging innovation to break down barriers and create more inclusive communities.</p>
                    <p>Through his leadership, AccessAdvisr continues to evolve as a platform that not only provides information but also uses advanced technology to improve the accessibility experience for users worldwide. Dr. Siddiqui's vision ensures that AccessAdvisr remains at the forefront of accessibility technology, constantly innovating to serve our community better.</p>
                    <p><a href="https://www.linkedin.com/in/dr-shah-siddiqui" target="_blank" class="text-decoration-none" style="color: #0077b5;">Learn more</a></p>
                </div>
                <div class="col-md-4">
                    <img src="/static/images/about/dr-shah-siddiqui.png" alt="Dr Shah Siddiqui" class="img-fluid rounded" style="width: 100%; max-width: 300px; height: auto;">
                </div>
            </div>
        </div>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='the-team-behind-accessadvisr',
            defaults={
                'title': 'The Team Behind AccessAdvisr',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published',
                'order': 0
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'The Team Behind AccessAdvisr'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))
        self.stdout.write(self.style.WARNING('\nNote: Please upload a featured image (handshake image) through the admin panel for this post.'))
    
    def create_environmental_post(self):
        content = """
        <h2>AccessAdvisr's Commitment to Sustainability</h2>
        
        <p>At AccessAdvisr, sustainability is a core principle that guides our actions and decisions. We believe that creating a more accessible world goes hand-in-hand with protecting our planet for future generations. Our commitment to environmental responsibility reflects our dedication to actions that benefit both people and the planet.</p>
        
        <h3>Minimizing Our Digital Footprint</h3>
        <p>We recognize that digital platforms have an environmental impact. To minimize our footprint, we use energy-efficient technologies, optimize our website performance, and host our systems on green-certified servers. We regularly audit our digital operations to identify opportunities for reducing energy consumption and carbon emissions.</p>
        
        <h3>Supporting Eco-Conscious Initiatives</h3>
        <p>AccessAdvisr actively supports and promotes eco-conscious initiatives that align with our mission. We collaborate with environmentally-aligned organizations and highlight accessible locations that prioritize sustainability. By connecting accessibility with environmental responsibility, we help our community make choices that are both inclusive and planet-friendly.</p>
        
        <h3>Fostering a Culture of Responsibility</h3>
        <p>Internally, we foster a culture of environmental responsibility among our team members. We encourage sustainable practices in our daily operations, from reducing paper usage to promoting remote work options that minimize commuting. Our team is committed to continuous improvement in our environmental practices.</p>
        
        <h3>The Link Between Sustainability and Accessibility</h3>
        <p>We recognize that sustainability and accessibility are interconnected. Creating inclusive spaces often involves thoughtful design that considers both environmental impact and accessibility needs. Many sustainable practices—such as walkable communities, public transportation, and energy-efficient buildings—also enhance accessibility for people with disabilities.</p>
        
        <h3>Continuous Improvement</h3>
        <p>Our commitment to environmental responsibility is ongoing. We regularly review and update our practices, seek feedback from our community, and stay informed about best practices in sustainable digital operations. We are committed to continuous improvement and advocacy for a more inclusive and sustainable future.</p>
        
        <p>Through our actions and advocacy, AccessAdvisr strives to demonstrate that accessibility and environmental responsibility can work together to create a better world for everyone.</p>
        """
        
        post, created = AboutPost.objects.get_or_create(
            slug='commitment-to-environmental-responsibility',
            defaults={
                'title': 'Commitment to Environmental Responsibility',
                'content': content.strip(),
                'share_this_post': True,
                'status': 'published'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created about post: {post.title}'))
        else:
            post.title = 'Commitment to Environmental Responsibility'
            post.content = content.strip()
            post.share_this_post = True
            post.status = 'published'
            post.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated about post: {post.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nPost URL: /about/{post.slug}/'))
        self.stdout.write(self.style.SUCCESS(f'Post ID: {post.id}'))

