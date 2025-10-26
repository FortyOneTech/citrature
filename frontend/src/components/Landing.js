import React from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpen, 
  Network, 
  Search, 
  MessageSquare, 
  Lightbulb, 
  ArrowRight,
  Upload,
  BarChart3,
  Brain,
  Target,
  Users,
  Zap
} from 'lucide-react';

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 via-white to-purple-50 opacity-50" />
        <div className="container mx-auto px-6 py-20 relative">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="flex-1 space-y-6">
              <div className="inline-flex items-center px-3 py-1 rounded-full bg-indigo-100 text-indigo-800 text-sm font-medium">
                <Zap className="h-4 w-4 mr-2" />
                AI-Powered Research Platform
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                Transform Research.
                <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent"> Discover Insights.</span>
                <br />Find Gaps.
              </h1>
              <p className="text-xl text-gray-600 max-w-xl">
                Upload PDFs, build citation graphs, chat with your research, and discover 
                research opportunities—all powered by AI and advanced analytics.
              </p>
              <div className="flex gap-4">
                <Link to="/login">
                  <button className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors group">
                    Get Started Free
                    <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </button>
                </Link>
                <button className="inline-flex items-center px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                  Watch Demo
                </button>
              </div>
              <div className="flex items-center gap-6 text-sm text-gray-500">
                <div className="flex items-center">
                  <Users className="h-4 w-4 mr-1" />
                  Free Plan Available
                </div>
                <div className="flex items-center">
                  <Brain className="h-4 w-4 mr-1" />
                  AI-Powered Analysis
                </div>
                <div className="flex items-center">
                  <Target className="h-4 w-4 mr-1" />
                  Research Gap Detection
                </div>
              </div>
            </div>
            <div className="flex-1">
              <div className="relative">
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 shadow-2xl">
                  <div className="bg-white rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <BookOpen className="h-6 w-6 text-indigo-600 mr-2" />
                      <h3 className="text-lg font-semibold">Research Collection</h3>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                          <span className="text-sm">Citation Graph Built</span>
                        </div>
                        <BarChart3 className="h-4 w-4 text-gray-400" />
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                          <span className="text-sm">AI Analysis Complete</span>
                        </div>
                        <Brain className="h-4 w-4 text-gray-400" />
                      </div>
                      <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
                          <span className="text-sm">Gap Analysis Ready</span>
                        </div>
                        <Lightbulb className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Everything You Need for Research</h2>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Four powerful features working together to accelerate your research workflow
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
            <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center mb-4">
              <Network className="h-6 w-6 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Citation Graphs</h3>
            <p className="text-gray-600">
              Build interactive citation networks with BFS/DFS traversal. Visualize how papers connect and influence each other.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
            <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
              <Search className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Smart Search</h3>
            <p className="text-gray-600">
              Hybrid BM25 + semantic search across your collection. Find relevant papers and sections instantly.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
              <MessageSquare className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI Chat</h3>
            <p className="text-gray-600">
              Ask questions and get answers with exact citations. Every claim links to source papers and sections.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
            <div className="w-12 h-12 rounded-lg bg-yellow-100 flex items-center justify-center mb-4">
              <Lightbulb className="h-6 w-6 text-yellow-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Gap Analysis</h3>
            <p className="text-gray-600">
              Discover ranked research opportunities with evidence. Find what's missing and where to contribute.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Simple, Powerful Workflow</h2>
            <p className="text-gray-600 text-lg">
              From sign-in to insights in minutes
            </p>
          </div>
          
          <div className="max-w-4xl mx-auto space-y-8">
            {[
              { 
                step: "01", 
                title: "Sign in & Create Collection", 
                desc: "One click with Google OAuth. Create your first research collection instantly.",
                icon: <Users className="h-6 w-6" />
              },
              { 
                step: "02", 
                title: "Upload Papers", 
                desc: "Upload PDFs or search for up to 30 papers by topic. Automatic deduplication and processing.",
                icon: <Upload className="h-6 w-6" />
              },
              { 
                step: "03", 
                title: "Build Citation Graph", 
                desc: "Choose BFS for breadth or DFS for depth. Visualize connections up to 3 levels deep.",
                icon: <BarChart3 className="h-6 w-6" />
              },
              { 
                step: "04", 
                title: "Chat & Explore", 
                desc: "Ask questions about your research, navigate the graph, and get AI-powered insights with citations.",
                icon: <MessageSquare className="h-6 w-6" />
              },
              { 
                step: "05", 
                title: "Discover Gaps", 
                desc: "Get ranked research opportunities with evidence. Find what's missing and jump back to sources.",
                icon: <Target className="h-6 w-6" />
              },
            ].map((item) => (
              <div key={item.step} className="flex gap-6 items-start">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 rounded-full bg-indigo-100 flex items-center justify-center">
                    <span className="text-2xl font-bold text-indigo-600">{item.step}</span>
                  </div>
                </div>
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center mr-3">
                      {item.icon}
                    </div>
                    <h3 className="text-xl font-semibold">{item.title}</h3>
                  </div>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Deep Dive */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Powerful Research Tools</h2>
          <p className="text-gray-600 text-lg">
            Advanced AI and analytics for modern researchers
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <h3 className="text-3xl font-bold mb-6">Citation Network Analysis</h3>
            <p className="text-gray-600 mb-6">
              Build comprehensive citation graphs that reveal the structure of knowledge in your field. 
              Use breadth-first or depth-first traversal to explore connections between papers.
            </p>
            <ul className="space-y-3">
              <li className="flex items-center">
                <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                Interactive graph visualization
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                Configurable traversal algorithms
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                Automatic citation resolution
              </li>
              <li className="flex items-center">
                <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                Export capabilities for further analysis
              </li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-8 text-white">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h4 className="text-lg font-semibold mb-4">Graph Statistics</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">127</div>
                  <div className="text-sm opacity-80">Papers</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">342</div>
                  <div className="text-sm opacity-80">Citations</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">3.2</div>
                  <div className="text-sm opacity-80">Avg Depth</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">89%</div>
                  <div className="text-sm opacity-80">Resolved</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Chat Section */}
      <section className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h3 className="text-3xl font-bold mb-6">AI-Powered Research Assistant</h3>
              <p className="text-gray-600 mb-6">
                Chat with your research collection using natural language. Get instant answers 
                with proper citations and source attribution.
              </p>
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                      <MessageSquare className="h-4 w-4 text-indigo-600" />
                    </div>
                    <span className="font-medium">User Question</span>
                  </div>
                  <p className="text-sm text-gray-600">"What are the main methodologies used in recent machine learning papers?"</p>
                </div>
                <div className="bg-indigo-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center mr-3">
                      <Brain className="h-4 w-4 text-indigo-600" />
                    </div>
                    <span className="font-medium">AI Response</span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">
                    Based on your collection, the main methodologies include deep learning (45%), 
                    reinforcement learning (23%), and transfer learning (18%)...
                  </p>
                  <div className="text-xs text-indigo-600">
                    Sources: Smith et al. (2023), Johnson & Lee (2022), Chen et al. (2023)
                  </div>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-3xl font-bold mb-6">Intelligent Research Analysis</h3>
              <p className="text-gray-600 mb-6">
                Our AI understands context, provides accurate answers, and always cites sources. 
                Perfect for literature reviews, gap analysis, and research planning.
              </p>
              <ul className="space-y-3">
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  Context-aware responses
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  Automatic source citation
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  Hybrid search capabilities
                </li>
                <li className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                  Research gap identification
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Transform Your Research?
          </h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Join researchers who are discovering literature faster with transparent, 
            citation-backed insights powered by AI.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <button className="inline-flex items-center px-8 py-4 bg-white text-indigo-600 rounded-lg hover:bg-gray-50 transition-colors font-semibold group">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>
            </Link>
            <button className="inline-flex items-center px-8 py-4 border-2 border-white text-white rounded-lg hover:bg-white/10 transition-colors font-semibold">
              Learn More
            </button>
          </div>
          <div className="mt-8 text-indigo-200 text-sm">
            <p>✓ Free plan available • ✓ No credit card required • ✓ Start in minutes</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <BookOpen className="h-8 w-8 text-indigo-400 mr-2" />
                <span className="text-xl font-bold">Citrature</span>
              </div>
              <p className="text-gray-400">
                AI-powered research paper analysis and citation graph platform.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Citation Graphs</li>
                <li>AI Chat</li>
                <li>Gap Analysis</li>
                <li>Smart Search</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Documentation</li>
                <li>API Reference</li>
                <li>Help Center</li>
                <li>Community</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400">
                <li>About</li>
                <li>Privacy</li>
                <li>Terms</li>
                <li>Contact</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Citrature. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
