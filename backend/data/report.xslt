<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" indent="yes" encoding="UTF-8"/>

  <xsl:template match="/">
    <html lang="en">
      <head>
        <meta charset="UTF-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <title>Library Dashboard Report</title>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
          h1 { font-size: 2rem; margin-bottom: 0.5rem; color: #38bdf8; }
          .subtitle { color: #94a3b8; margin-bottom: 2rem; }
          .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
          .stat-card { background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }
          .stat-card .value { font-size: 2.5rem; font-weight: 700; color: #38bdf8; }
          .stat-card .label { color: #94a3b8; font-size: 0.875rem; margin-top: 0.25rem; }
          section { margin-bottom: 2rem; }
          h2 { font-size: 1.25rem; color: #f1f5f9; margin-bottom: 1rem; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }
          table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }
          th { background: #334155; text-align: left; padding: 0.75rem 1rem; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
          td { padding: 0.75rem 1rem; border-top: 1px solid #334155; }
          tr:hover td { background: #263548; }
          .badge { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
          .badge-sci-fi { background: #1e3a5f; color: #7dd3fc; }
          .badge-fantasy { background: #3b1f6e; color: #c4b5fd; }
          .badge-tech { background: #1a3a2a; color: #86efac; }
          .badge-classic { background: #3b2f1a; color: #fcd34d; }
          .badge-default { background: #334155; color: #cbd5e1; }
          .status-active { color: #4ade80; }
          .status-overdue { color: #f87171; }
          .status-returned { color: #94a3b8; }
          footer { text-align: center; color: #64748b; font-size: 0.875rem; margin-top: 2rem; }
        </style>
      </head>
      <body>
        <h1>Library Dashboard Report</h1>
        <p class="subtitle">
          <xsl:value-of select="/library/@name"/> —
          Generated via XSLT transformation
        </p>

        <div class="stats">
          <div class="stat-card">
            <div class="value"><xsl:value-of select="count(/library/books/book)"/></div>
            <div class="label">Total Books</div>
          </div>
          <div class="stat-card">
            <div class="value"><xsl:value-of select="count(/library/members/member)"/></div>
            <div class="label">Registered Members</div>
          </div>
          <div class="stat-card">
            <div class="value"><xsl:value-of select="count(/library/borrowings/borrowing[status='active'])"/></div>
            <div class="label">Active Borrowings</div>
          </div>
          <div class="stat-card">
            <div class="value"><xsl:value-of select="count(/library/borrowings/borrowing[status='overdue'])"/></div>
            <div class="label">Overdue Items</div>
          </div>
          <div class="stat-card">
            <div class="value"><xsl:value-of select="count(/library/books/book[categories/category='Sci-Fi'])"/></div>
            <div class="label">Sci-Fi Books</div>
          </div>
          <div class="stat-card">
            <div class="value"><xsl:value-of select="sum(/library/books/book/availableCopies)"/></div>
            <div class="label">Total Available Copies</div>
          </div>
        </div>

        <section>
          <h2>Book Catalog</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Category</th>
                <th>Year</th>
                <th>Copies</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="/library/books/book">
                <xsl:sort select="title"/>
                <tr>
                  <td><xsl:value-of select="@id"/></td>
                  <td><strong><xsl:value-of select="title"/></strong></td>
                  <td><xsl:value-of select="author"/></td>
                  <td>
                    <span class="badge badge-default">
                      <xsl:value-of select="categories/category[1]"/>
                    </span>
                  </td>
                  <td><xsl:value-of select="publicationYear"/></td>
                  <td><xsl:value-of select="availableCopies"/></td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </section>

        <section>
          <h2>Active &amp; Overdue Borrowings</h2>
          <table>
            <thead>
              <tr>
                <th>Borrowing ID</th>
                <th>Book</th>
                <th>Member</th>
                <th>Borrow Date</th>
                <th>Due Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="/library/borrowings/borrowing[status='active' or status='overdue']">
                <tr>
                  <td><xsl:value-of select="@id"/></td>
                  <td>
                    <xsl:value-of select="/library/books/book[@id=current()/@bookRef]/title"/>
                  </td>
                  <td>
                    <xsl:value-of select="/library/members/member[@id=current()/@memberRef]/firstName"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="/library/members/member[@id=current()/@memberRef]/lastName"/>
                  </td>
                  <td><xsl:value-of select="borrowDate"/></td>
                  <td><xsl:value-of select="dueDate"/></td>
                  <td>
                    <span>
                      <xsl:attribute name="class">
                        status-<xsl:value-of select="status"/>
                      </xsl:attribute>
                      <xsl:value-of select="status"/>
                    </span>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </section>

        <section>
          <h2>Members Overview</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Type</th>
                <th>Active / Overdue Loans</th>
              </tr>
            </thead>
            <tbody>
              <xsl:for-each select="/library/members/member">
                <tr>
                  <td><xsl:value-of select="@id"/></td>
                  <td>
                    <xsl:value-of select="firstName"/>
                    <xsl:text> </xsl:text>
                    <xsl:value-of select="lastName"/>
                  </td>
                  <td><xsl:value-of select="email"/></td>
                  <td><xsl:value-of select="membershipType"/></td>
                  <td>
                    <xsl:value-of select="count(/library/borrowings/borrowing[@memberRef=current()/@id and (status='active' or status='overdue')])"/>
                  </td>
                </tr>
              </xsl:for-each>
            </tbody>
          </table>
        </section>

        <footer>
          XML Library Management System — XSLT Report
        </footer>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
