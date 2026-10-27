import React, { useState } from 'react';
import {
  Building2, GraduationCap, Upload, CheckCircle2, ArrowRight, ArrowLeft,
  FileText, Trash2, AlertCircle, Sparkles, Check, FileCheck
} from 'lucide-react';
import { api } from '../services/api';
import { User, ApplicationItem } from '../types';

interface SubmitApplicationPageProps {
  user: User;
  onNavigate: (path: string) => void;
  onApplicationCreated: (id: number) => void;
}

export const SubmitApplicationPage: React.FC<SubmitApplicationPageProps> = ({
  user,
  onNavigate,
  onApplicationCreated
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Institution Details
  const [instName, setInstName] = useState(user.full_name.includes('Apex') ? 'Apex Institute of Technology & Engineering' : 'National Institute of Technology');
  const [instCode, setInstCode] = useState('INST-TECH-2026');
  const [instType, setInstType] = useState('Engineering & Technology');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [address, setAddress] = useState('Survey 42/1, Hinjawadi Phase 2, Pune, Maharashtra 411057');
  const [contactEmail, setContactEmail] = useState(user.email);
  const [contactPhone, setContactPhone] = useState('+91-20-88997701');

  // Step 2: Academic & Infrastructure
  const [courses, setCourses] = useState([
    { name: 'Computer Science & Engineering', intake: 120 },
    { name: 'Artificial Intelligence & Machine Learning', intake: 60 }
  ]);
  const [newCourseName, setNewCourseName] = useState('');
  const [newCourseIntake, setNewCourseIntake] = useState(60);
  const [studentIntake, setStudentIntake] = useState(180);
  const [facultyCount, setFacultyCount] = useState(12);
  const [campusAreaAcres, setCampusAreaAcres] = useState(6.5);
  const [builtUpAreaSqm, setBuiltUpAreaSqm] = useState(11500);

  // Step 3: Document Uploads
  const [filesToUpload, setFilesToUpload] = useState<{
    file: File;
    documentType: string;
  }[]>([]);
  const [selectedDocType, setSelectedDocType] = useState('Registration Certificate');

  // Completed Application
  const [submittedApp, setSubmittedApp] = useState<ApplicationItem | null>(null);

  const addCourse = () => {
    if (!newCourseName.trim()) return;
    const updated = [...courses, { name: newCourseName.trim(), intake: Number(newCourseIntake) }];
    setCourses(updated);
    setStudentIntake(updated.reduce((sum, c) => sum + c.intake, 0));
    setNewCourseName('');
  };

  const removeCourse = (idx: number) => {
    const updated = courses.filter((_, i) => i !== idx);
    setCourses(updated);
    setStudentIntake(updated.reduce((sum, c) => sum + c.intake, 0));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    setFilesToUpload(prev => [...prev, { file, documentType: selectedDocType }]);
    e.target.value = '';
  };

  const removeFile = (idx: number) => {
    setFilesToUpload(prev => prev.filter((_, i) => i !== idx));
  };

  const handleFinalSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Create Application
      const newApp = await api.createApplication({
        academic_year: '2026-2027',
        courses_offered: courses,
        student_intake: studentIntake,
        faculty_count: facultyCount,
        campus_area_acres: campusAreaAcres,
        built_up_area_sqm: builtUpAreaSqm
      });

      // 2. Upload attached documents if any
      for (const item of filesToUpload) {
        await api.uploadDocument(newApp.id, item.documentType, item.file);
      }

      // 3. Submit & Trigger AI pipeline
      await api.submitApplication(newApp.id);
      const finalized = await api.getApplication(newApp.id);
      setSubmittedApp(finalized);
      setCurrentStep(5);
    } catch (e: any) {
      setError(e.message || 'Failed to submit application');
    } finally {
      setLoading(false);
    }
  };

  const DOCUMENT_CATEGORIES = [
    'Registration Certificate',
    'Land Document',
    'Building Safety',
    'Faculty Qualification',
    'AICTE Mandatory Disclosure',
    'Financial Audit / Balance Sheet'
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Wizard Progress Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4 mb-4">
          <div>
            <h1 className="text-xl font-bold text-navy-900">
              Institutional Regulatory Application
            </h1>
            <p className="text-xs text-slate-500">
              AICTE Approval Process Handbook (APH) Verification Cycle 2026-2027
            </p>
          </div>
          <div className="text-xs font-mono font-bold text-royal-600 bg-royal-50 px-3 py-1.5 rounded-xl border border-royal-200">
            STEP {currentStep} OF 5
          </div>
        </div>

        {/* Stepper Dots */}
        <div className="grid grid-cols-5 gap-2 text-center text-xs">
          {[
            { step: 1, label: 'Institution' },
            { step: 2, label: 'Academics & Infra' },
            { step: 3, label: 'Documents' },
            { step: 4, label: 'Pre-Check' },
            { step: 5, label: 'Complete' }
          ].map((s) => (
            <div key={s.step} className="flex flex-col items-center">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs mb-1 transition-all ${
                  currentStep > s.step
                    ? 'bg-emerald-500 text-white'
                    : currentStep === s.step
                    ? 'bg-royal-600 text-white ring-4 ring-royal-100'
                    : 'bg-slate-200 text-slate-500'
                }`}
              >
                {currentStep > s.step ? <Check className="w-3.5 h-3.5" /> : s.step}
              </div>
              <span className={`text-[10px] hidden sm:block ${currentStep === s.step ? 'font-bold text-navy-900' : 'text-slate-400'}`}>
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* STEP 1: Institution Details */}
      {currentStep === 1 && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Building2 className="w-5 h-5 text-royal-600" />
            <h2 className="font-bold text-base text-navy-900">Step 1: Institution Basic Details</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="sm:col-span-2">
              <label className="block font-semibold text-navy-900 mb-1">Official Institution Name</label>
              <input
                type="text"
                value={instName}
                onChange={e => setInstName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
              <p className="text-[10px] text-slate-400 mt-0.5">Must match state registration or society deed name.</p>
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Institution Code / Permanent ID</label>
              <input
                type="text"
                value={instCode}
                onChange={e => setInstCode(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Institution Category / Program</label>
              <select
                value={instType}
                onChange={e => setInstType(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none bg-white"
              >
                <option>Engineering & Technology</option>
                <option>Management & MBA</option>
                <option>Polytechnic & Diploma</option>
                <option>Pharmacy</option>
                <option>MCA / Computer Applications</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">State</label>
              <input
                type="text"
                value={state}
                onChange={e => setState(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">District</label>
              <input
                type="text"
                value={district}
                onChange={e => setDistrict(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block font-semibold text-navy-900 mb-1">Complete Campus Address</label>
              <textarea
                rows={2}
                value={address}
                onChange={e => setAddress(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Official Contact Email</label>
              <input
                type="email"
                value={contactEmail}
                onChange={e => setContactEmail(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Official Telephone</label>
              <input
                type="text"
                value={contactPhone}
                onChange={e => setContactPhone(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentStep(2)}
              className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md transition-all"
            >
              <span>Continue to Step 2: Academics & Infra</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Academics & Infrastructure */}
      {currentStep === 2 && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <GraduationCap className="w-5 h-5 text-royal-600" />
            <h2 className="font-bold text-base text-navy-900">Step 2: Academic Programs & Campus Infrastructure</h2>
          </div>

          {/* Courses List */}
          <div className="space-y-3">
            <label className="block font-semibold text-xs text-navy-900">Approved Courses Offered & Student Intake</label>
            <div className="space-y-2">
              {courses.map((c, i) => (
                <div key={i} className="flex items-center justify-between p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-royal-100 text-royal-700 font-bold flex items-center justify-center text-[10px]">
                      {i + 1}
                    </span>
                    <span className="font-semibold text-navy-900">{c.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-slate-600">Intake: <strong>{c.intake}</strong></span>
                    <button
                      onClick={() => removeCourse(i)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-2 pt-1">
              <input
                type="text"
                placeholder="Course Name (e.g. Mechanical Engineering)"
                value={newCourseName}
                onChange={e => setNewCourseName(e.target.value)}
                className="flex-1 px-3 py-1.5 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-royal-500"
              />
              <input
                type="number"
                placeholder="Intake"
                value={newCourseIntake}
                onChange={e => setNewCourseIntake(Number(e.target.value))}
                className="w-24 px-3 py-1.5 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-royal-500"
              />
              <button
                type="button"
                onClick={addCourse}
                className="bg-royal-50 hover:bg-royal-100 text-royal-700 border border-royal-300 px-3 py-1.5 rounded-xl text-xs font-semibold"
              >
                Add Course
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
            <div>
              <label className="block font-semibold text-navy-900 mb-1">Total Approved Student Intake</label>
              <input
                type="number"
                value={studentIntake}
                onChange={e => setStudentIntake(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Total Full-Time Teaching Faculty</label>
              <input
                type="number"
                value={facultyCount}
                onChange={e => setFacultyCount(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
              <p className="text-[10px] text-slate-400 mt-0.5">
                Calculated SFR: <strong>1:{facultyCount > 0 ? (studentIntake / facultyCount).toFixed(1) : 0}</strong> (Norm: max 1:20)
              </p>
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Contiguous Campus Land Area (Acres)</label>
              <input
                type="number"
                step="0.1"
                value={campusAreaAcres}
                onChange={e => setCampusAreaAcres(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
              <p className="text-[10px] text-slate-400 mt-0.5">Norm: Min 5.0 Acres for Non-Metro Technical campuses.</p>
            </div>

            <div>
              <label className="block font-semibold text-navy-900 mb-1">Instructional Built-Up Area (sq. meters)</label>
              <input
                type="number"
                value={builtUpAreaSqm}
                onChange={e => setBuiltUpAreaSqm(Number(e.target.value))}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl font-mono focus:ring-2 focus:ring-royal-500 focus:outline-none"
              />
              <p className="text-[10px] text-slate-400 mt-0.5">Norm: Min 10,000 sqm for engineering programs.</p>
            </div>
          </div>

          <div className="flex justify-between pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentStep(1)}
              className="flex items-center gap-1.5 text-slate-600 hover:text-navy-900 font-semibold text-xs px-4 py-2.5"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              onClick={() => setCurrentStep(3)}
              className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md transition-all"
            >
              <span>Continue to Step 3: Document Uploads</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Document Upload */}
      {currentStep === 3 && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <Upload className="w-5 h-5 text-royal-600" />
            <h2 className="font-bold text-base text-navy-900">Step 3: Statutory Document Upload</h2>
          </div>

          <div className="bg-blue-50/60 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 space-y-1">
            <div className="font-bold flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-royal-600" />
              <span>Automated OCR & Cross-Document Parsing Enabled</span>
            </div>
            <p className="text-[11px] text-blue-700">
              Attached documents will be processed by VerifyAI OCR engine to extract entity names, registration codes, issue dates, and land records for consistency validation. Supported formats: PDF, PNG, JPG (Max 25MB).
            </p>
          </div>

          {/* Upload Control */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
            <div className="sm:col-span-2">
              <label className="block font-semibold text-xs text-navy-900 mb-1">Select Document Category</label>
              <select
                value={selectedDocType}
                onChange={e => setSelectedDocType(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-royal-500 bg-white"
              >
                {DOCUMENT_CATEGORIES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="flex items-center justify-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs py-2 px-4 rounded-xl cursor-pointer shadow-md transition-all">
                <Upload className="w-4 h-4" />
                <span>Choose File</span>
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          {/* Uploaded Files Table */}
          <div className="border border-slate-200 rounded-xl overflow-hidden text-xs">
            <div className="bg-slate-50 px-4 py-2.5 font-semibold text-slate-700 border-b border-slate-200 flex justify-between">
              <span>Attached Documents ({filesToUpload.length})</span>
              <span className="text-[11px] text-slate-500 font-normal">Pre-upload Queue</span>
            </div>

            {filesToUpload.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                <p>No documents attached yet.</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Please upload required statutory documents (Registration Certificate, Land Title Deed, Building Safety NOC).</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {filesToUpload.map((item, idx) => (
                  <div key={idx} className="p-3 flex items-center justify-between hover:bg-slate-50">
                    <div className="flex items-center gap-3">
                      <FileCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                      <div>
                        <div className="font-semibold text-navy-900">{item.file.name}</div>
                        <div className="text-[10px] text-slate-500">
                          Category: <span className="text-royal-600 font-medium">{item.documentType}</span> &bull; {(item.file.size / 1024).toFixed(1)} KB
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex justify-between pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentStep(2)}
              className="flex items-center gap-1.5 text-slate-600 hover:text-navy-900 font-semibold text-xs px-4 py-2.5"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back</span>
            </button>
            <button
              onClick={() => setCurrentStep(4)}
              className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md transition-all"
            >
              <span>Review & Pre-Check</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Review & Pre-validation */}
      {currentStep === 4 && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <h2 className="font-bold text-base text-navy-900">Step 4: Final Application Review & Automated Pre-Check</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
              <span className="font-bold text-slate-500 text-[10px] uppercase font-mono">Institution Summary</span>
              <div className="text-sm font-bold text-navy-900">{instName}</div>
              <div className="text-slate-600">{instType} &bull; Code: {instCode}</div>
              <div className="text-slate-500">{district}, {state}</div>
              <div className="text-slate-500">{contactEmail} &bull; {contactPhone}</div>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
              <span className="font-bold text-slate-500 text-[10px] uppercase font-mono">Academic & Infrastructure</span>
              <div className="text-slate-700">Total Student Intake: <strong>{studentIntake}</strong></div>
              <div className="text-slate-700">Teaching Faculty: <strong>{facultyCount}</strong> (SFR: 1:{(studentIntake / Math.max(facultyCount, 1)).toFixed(1)})</div>
              <div className="text-slate-700">Campus Land Area: <strong>{campusAreaAcres} Acres</strong></div>
              <div className="text-slate-700">Built-Up Area: <strong>{builtUpAreaSqm.toLocaleString()} sqm</strong></div>
            </div>
          </div>

          {/* Pre-check notice */}
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 space-y-1">
            <div className="font-bold flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-amber-600" />
              <span>Submission Pre-Check Confirmation</span>
            </div>
            <p className="text-[11px] text-amber-800">
              Upon clicking "Submit & Run AI Verification", your application will be assigned an official AICTE Reference ID. The document intelligence engine will parse your files, run cross-consistency audits, and evaluate compliance against configured statutory rules.
            </p>
          </div>

          <div className="flex justify-between pt-4 border-t border-slate-100">
            <button
              onClick={() => setCurrentStep(3)}
              className="flex items-center gap-1.5 text-slate-600 hover:text-navy-900 font-semibold text-xs px-4 py-2.5"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Documents</span>
            </button>
            <button
              onClick={handleFinalSubmit}
              disabled={loading}
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs px-6 py-2.5 rounded-xl shadow-md shadow-emerald-600/30 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? 'Processing Documents & AI Rules...' : 'Submit & Run AI Verification'}</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: Success & Unique Reference ID Generation */}
      {currentStep === 5 && submittedApp && (
        <div className="bg-white p-8 sm:p-12 rounded-2xl border border-slate-200 shadow-xl text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-inner">
            <CheckCircle2 className="w-10 h-10" />
          </div>

          <div>
            <span className="text-xs font-mono font-bold uppercase text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              APPLICATION SUBMITTED SUCCESSFULLY
            </span>
            <h2 className="text-2xl font-extrabold text-navy-900 mt-2">
              Reference ID: <span className="font-mono text-royal-600">{submittedApp.reference_id}</span>
            </h2>
            <p className="text-xs text-slate-500 mt-2 max-w-md mx-auto">
              Your institutional application has been encrypted, stored, and processed through the VerifyAI Scrutiny Pipeline.
            </p>
          </div>

          {/* AI Scorecard Preview */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 max-w-md mx-auto text-left text-xs space-y-3">
            <div className="flex justify-between items-center border-b border-slate-200 pb-2">
              <span className="font-semibold text-slate-500">Regulatory Compliance Score</span>
              <span className="font-mono font-extrabold text-sm text-navy-900">{submittedApp.compliance_score}%</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-200 pb-2">
              <span className="font-semibold text-slate-500">Risk Profile Assessment</span>
              <span className={`font-mono font-bold uppercase ${submittedApp.risk_level === 'low' ? 'text-emerald-600' : 'text-amber-600'}`}>
                {submittedApp.risk_level} Risk
              </span>
            </div>
            <div>
              <span className="font-semibold text-slate-500 block mb-1">AI Validation Summary</span>
              <p className="text-[11px] text-slate-700 leading-relaxed bg-white p-2.5 rounded-lg border border-slate-200">
                {submittedApp.ai_validation_summary || 'Document verification completed without automated blockers.'}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onApplicationCreated(submittedApp.id)}
              className="flex items-center gap-2 bg-royal-600 hover:bg-royal-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-md transition-all"
            >
              <span>View Application Inspection</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <a
              href={api.getComplianceReportUrl(submittedApp.id)}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs px-5 py-2.5 rounded-xl border border-slate-300 transition-colors"
            >
              <FileCheck className="w-4 h-4 text-slate-600" />
              <span>Download PDF Report</span>
            </a>
          </div>
        </div>
      )}
    </div>
  );
};
