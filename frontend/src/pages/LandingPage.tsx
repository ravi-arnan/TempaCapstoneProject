import { Link } from "react-router-dom";
import { 
  FileText, 
  Link as LinkIcon, 
  Brain, 
  LineChart, 
  Zap, 
  Trophy,
  ArrowRight
} from "lucide-react";

export function LandingPage() {
  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="text-center space-y-6">
        <h1 className="text-5xl md:text-6xl font-medium leading-[1.05] tracking-tight text-text-primary">
          Asah lagi sampai paham.
        </h1>
        <p className="max-w-2xl mx-auto text-lg md:text-xl text-text-secondary">
          Sistem deteksi tingkat pemahaman yang mengubah materi belajarmu menjadi kuis interaktif, menganalisis hasilnya, dan memberikan rekomendasi personal.
        </p>
        <div className="pt-4">
          <Link
            to="/app"
            className="inline-flex items-center gap-2 rounded-full border border-brand-button bg-brand-button px-6 py-3 text-base font-medium text-white shadow-level-2 outline-none transition-colors hover:bg-emerald-600 focus-visible:[box-shadow:var(--focus-ring)]"
          >
            Coba sekarang
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="space-y-8">
        <h2 className="text-3xl font-medium text-center text-text-primary">Cara Kerja</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <StepCard 
            number="1"
            title="Pilih Materi"
            description="Masukkan teks, paste URL artikel, atau upload file PDF yang ingin kamu pelajari."
          />
          <StepCard 
            number="2"
            title="Kerjakan Kuis"
            description="Jawab pertanyaan satu-per-satu yang dibuat otomatis berdasarkan materimu."
          />
          <StepCard 
            number="3"
            title="Lihat Analisis"
            description="Dapatkan insight tentang tingkat pemahamanmu dan rekomendasi langkah selanjutnya."
          />
        </div>
      </section>

      {/* Features Grid */}
      <section className="space-y-8">
        <h2 className="text-3xl font-medium text-center text-text-primary">Fitur Unggulan</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard 
            icon={<FileText className="h-6 w-6 text-brand-button" />}
            title="Input Multi-source"
            description="Mendukung materi dari teks langsung, link web, maupun dokumen PDF."
          />
          <FeatureCard 
            icon={<Brain className="h-6 w-6 text-brand-button" />}
            title="Kuis Terfokus"
            description="Satu pertanyaan setiap waktu agar kamu bisa fokus penuh tanpa terdistraksi."
          />
          <FeatureCard 
            icon={<LineChart className="h-6 w-6 text-brand-button" />}
            title="Analisis Pemahaman"
            description="Tidak hanya skor, tapi deteksi seberapa jauh tingkat pemahamanmu."
          />
          <FeatureCard 
            icon={<Zap className="h-6 w-6 text-brand-button" />}
            title="Insight & Rekomendasi"
            description="Umpan balik personal berdasarkan pola jawaban dan kecepatan menjawabmu."
          />
          <FeatureCard 
            icon={<Trophy className="h-6 w-6 text-brand-button" />}
            title="Gamifikasi Seru"
            description="Kumpulkan XP, pertahankan streak harian, dan raih badge pencapaian."
          />
          <FeatureCard 
            icon={<LinkIcon className="h-6 w-6 text-brand-button" />}
            title="Mastery Per-topik"
            description="Lacak perkembangan pemahamanmu untuk berbagai topik berbeda dari waktu ke waktu."
          />
        </div>
      </section>
    </div>
  );
}

function StepCard({ number, title, description }: { number: string, title: string, description: string }) {
  return (
    <div className="flex flex-col items-center text-center space-y-3 p-6 rounded-2xl border border-border-standard bg-bg-page shadow-level-1">
      <div className="flex items-center justify-center h-12 w-12 rounded-full bg-brand-button text-white font-bold text-xl mb-2">
        {number}
      </div>
      <h3 className="text-xl font-medium text-text-primary">{title}</h3>
      <p className="text-text-secondary leading-relaxed">{description}</p>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="p-6 rounded-2xl border border-border-standard bg-bg-page shadow-level-1 text-left space-y-3 hover:border-brand-button transition-colors">
      <div className="h-10 w-10 flex items-center justify-center rounded-lg bg-bg-alt">
        {icon}
      </div>
      <h3 className="text-lg font-medium text-text-primary">{title}</h3>
      <p className="text-text-secondary text-sm leading-relaxed">{description}</p>
    </div>
  );
}
