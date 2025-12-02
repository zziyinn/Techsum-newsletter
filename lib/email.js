// lib/email.js
/**
 * 发送邮件工具函数
 * 使用 Gmail SMTP 发送邮件
 */

import nodemailer from 'nodemailer';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let transporter = null;

function getTransporter() {
  if (transporter) return transporter;
  
  const user = process.env.EMAIL_USER;
  const pass = process.env.EMAIL_PASS;
  
  if (!user || !pass) {
    console.warn('[email] EMAIL_USER or EMAIL_PASS not set, email sending disabled');
    return null;
  }
  
  transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user,
      pass
    }
  });
  
  return transporter;
}

/**
 * 发送确认邮件给新订阅者
 */
export async function sendConfirmationEmail(email) {
  const trans = getTransporter();
  if (!trans) {
    console.warn('[email] Cannot send confirmation email: transporter not configured');
    return false;
  }
  
  try {
    // 读取确认邮件模板
    const templatePath = join(__dirname, '..', 'src', 'confirmation_email_template.html');
    let template = readFileSync(templatePath, 'utf-8');
    
    // 替换模板变量
    const unsubUrl = process.env.UNSUB_URL || 'https://web-production-914f7.up.railway.app/unsubscribe.html';
    template = template.replace(/\{\{UNSUB_URL\}\}/g, unsubUrl);
    template = template.replace(/\{\{EMAIL\}\}/g, encodeURIComponent(email));
    
    const confirmationHtml = template;
    
    const info = await trans.sendMail({
      from: `"TechSum" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: '🎉 Welcome to TechSum Newsletter!',
      html: confirmationHtml
    });
    
    console.log(`[email] Confirmation email sent to ${email}:`, info.messageId);
    return true;
  } catch (error) {
    console.error(`[email] Failed to send confirmation email to ${email}:`, error);
    return false;
  }
}

