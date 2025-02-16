import {
  Cloud,
  CloudLightning,
  Code,
  Database,
  Server,
  Shield,
} from "lucide-react";

const certifications = [
  {
    title: "Cloud Practitioner",
    description: "Foundational understanding of AWS Cloud concepts",
    icon: Cloud,
  },
  {
    title: "Solutions Architect",
    description: "Design distributed systems on AWS",
    icon: CloudLightning,
  },
  {
    title: "Developer",
    description: "Build and deploy applications on AWS",
    icon: Code,
  },
  {
    title: "SysOps Administrator",
    description: "Manage and operate systems on AWS",
    icon: Server,
  },
  {
    title: "Database Specialty",
    description: "Expertise in AWS database services",
    icon: Database,
  },
  {
    title: "Security Specialty",
    description: "Secure AWS applications and infrastructure",
    icon: Shield,
  },
];

interface CertificationCardProps {
  title: string;
  description: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

const CertificationCard: React.FC<CertificationCardProps> = ({
  title,
  description,
  icon: Icon,
}) => (
  <div className="bg-white rounded-lg shadow-md p-6 flex flex-col items-center transition-transform hover:scale-105 cursor-pointer">
    <Icon className="w-12 h-12 text-blue-500 mb-4" />
    <h3 className="text-xl font-semibold mb-2 text-center">{title}</h3>
    <p className="text-gray-600 text-center">{description}</p>
  </div>
);

const QuizStart = () => {
  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            AWS Certification Quiz Selection
          </h1>
          <p className="text-xl text-gray-600">
            Choose a certification to start your quiz
          </p>
        </header>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {certifications.map((cert, index) => (
            <CertificationCard key={index} {...cert} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default QuizStart;
