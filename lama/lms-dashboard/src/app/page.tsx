import Cursor from "@/components/landing/Cursor";
import ScrollProgress from "@/components/landing/ScrollProgress";
import Nav from "@/components/landing/Nav";
import Hero from "@/components/landing/Hero";
import Pipeline from "@/components/landing/Pipeline";
import Portals from "@/components/landing/Portals";
import Stats from "@/components/landing/Stats";
import CTAFooter from "@/components/landing/CTAFooter";

export default function Home() {
  return (
    <main className="cursor-none-desktop bg-paper">
      <Cursor />
      <ScrollProgress />
      <Nav />
      <Hero />
      <Pipeline />
      <Portals />
      <Stats />
      <CTAFooter />
    </main>
  );
}
